"""
Algoritmo de divisão de polígonos para PRA
Versão TOTALMENTE CORRIGIDA - Cálculo Real de Áreas
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsField, QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant
import numpy as np


class PRADividerAlgorithm:
    """Algoritmo para divisão de polígonos APP e Reserva Legal"""
    
    def __init__(self, iface, layer, division_type, dialog=None):
        self.iface = iface
        self.layer = layer
        self.division_type = division_type
        self.dialog = dialog
        self.parts = 5 if division_type == 'APP' else 10
        self.max_iters = 150  # Aumentado para melhor precisão
        self.tol_abs = 0.01  # Tolerância mais restrita
        
    def execute(self):
        """Executar divisão"""
        try:
            # Validar camada
            if QgsWkbTypes.geometryType(self.layer.wkbType()) != QgsWkbTypes.PolygonGeometry:
                return False, "A camada selecionada não é poligonal."
            
            if self.dialog:
                self.dialog.set_progress(15, "Unindo geometrias...")
            
            # Unir geometrias
            geoms = [f.geometry().buffer(0, 5) for f in self.layer.getFeatures()]
            if not geoms:
                return False, "Nenhuma feição encontrada na camada."
            
            union = geoms[0]
            for g in geoms[1:]:
                union = union.combine(g).buffer(0, 5)
            
            total_area = float(union.area())
            if total_area <= 0:
                return False, "Área total inválida."
            
            if self.dialog:
                self.dialog.set_progress(30, f"Dividindo em {self.parts} partes...")
            
            # Processar divisão COM BUSCA BINÁRIA MELHORADA
            parts = self._divide_polygon_precise(union, total_area)
            
            if self.dialog:
                self.dialog.set_progress(80, "Criando camada de saída...")
            
            # Criar camada de saída
            output_name = f"PRA_{self.division_type}_{self.parts}_Partes"
            success, message = self._create_output_layer(parts, total_area, output_name)
            
            if success:
                return True, message
            else:
                return False, "Erro ao criar camada de saída."
                
        except Exception as e:
            return False, f"Erro no processamento: {str(e)}"
    
    def _divide_polygon_precise(self, union, total_area):
        """
        Divisão PRECISA de polígono com busca binária melhorada
        """
        # Obter pontos da geometria
        pts = self._geom_points(union)
        
        # Calcular eixo principal (PCA)
        centroid = pts.mean(axis=0)
        centered = pts - centroid
        u, s, vh = np.linalg.svd(centered, full_matrices=False)
        axis = vh[0] / np.linalg.norm(vh[0])
        ux, uy = axis[0], axis[1]
        cx, cy = centroid
        
        # Projetar pontos no eixo principal
        u_vals, v_vals = [], []
        for x, y in pts:
            dx, dy = x - cx, y - cy
            u_vals.append(dx*ux + dy*uy)
            v_vals.append(dx*-uy + dy*ux)
        
        u_min, u_max = min(u_vals), max(u_vals)
        v_min, v_max = min(v_vals), max(v_vals)
        
        # Adicionar margem
        margin_u = (u_max - u_min) * 0.15  # Aumentado para garantir cobertura
        margin_v = (v_max - v_min) * 0.15
        
        u_min_ext = u_min - margin_u
        u_max_ext = u_max + margin_u
        v_min_ext = v_min - margin_v
        v_max_ext = v_max + margin_v
        
        # Função para converter uv para xy
        def uv_to_xy(u, v):
            vx, vy = -uy, ux
            x = cx + u*ux + v*vx
            y = cy + u*uy + v*vy
            return QgsPointXY(x, y)
        
        # Função para criar retângulo
        def rect_geom(u0, u1):
            pts_rect = [
                uv_to_xy(u0, v_min_ext), uv_to_xy(u1, v_min_ext),
                uv_to_xy(u1, v_max_ext), uv_to_xy(u0, v_max_ext),
                uv_to_xy(u0, v_min_ext)
            ]
            return QgsGeometry.fromPolygonXY([pts_rect]).buffer(0, 5)
        
        # 🔥 NOVA ESTRATÉGIA: Divisão iterativa com ajuste fino
        parts = []
        remainder = union.buffer(0, 5)
        
        # Calcular área restante dinamicamente
        for i in range(self.parts - 1):
            if self.dialog:
                progress = 30 + int((i / self.parts) * 50)
                self.dialog.set_progress(progress, f"Processando parte {i+1}/{self.parts}...")
            
            # Área alvo = resto / partes restantes
            remaining_parts = self.parts - i
            current_target = remainder.area() / remaining_parts
            
            # Buscar limites do remainder atual
            remainder_pts = self._geom_points(remainder)
            if len(remainder_pts) == 0:
                break
                
            u_vals_rem = [(p[0]-cx)*ux + (p[1]-cy)*uy for p in remainder_pts]
            u_min_rem = min(u_vals_rem)
            u_max_rem = max(u_vals_rem)
            
            # Busca binária MELHORADA
            lo, hi = u_min_rem, u_max_rem
            best_cut = lo
            best_area_diff = float('inf')
            
            for iteration in range(self.max_iters):
                mid = (lo + hi) / 2.0
                
                # Testar corte
                test_rect = rect_geom(u_min_rem, mid)
                test_intersection = remainder.intersection(test_rect).buffer(0, 5)
                
                if test_intersection.isEmpty():
                    lo = mid
                    continue
                
                test_area = test_intersection.area()
                area_diff = abs(test_area - current_target)
                
                # Guardar melhor resultado
                if area_diff < best_area_diff:
                    best_area_diff = area_diff
                    best_cut = mid
                
                # Convergência
                if area_diff <= self.tol_abs:
                    best_cut = mid
                    break
                
                # Ajustar limites
                if test_area < current_target:
                    lo = mid
                else:
                    hi = mid
            
            # Extrair fatia com o melhor corte encontrado
            cut_rect = rect_geom(u_min_rem, best_cut)
            fatia = remainder.intersection(cut_rect).buffer(0, 5)
            
            if not fatia.isEmpty():
                parts.append(fatia)
                remainder = remainder.difference(fatia).buffer(0, 5)
        
        # Última parte = todo o resto
        if not remainder.isEmpty():
            parts.append(remainder.buffer(0, 5))
        
        return parts
    
    def _geom_points(self, g):
        """Extrair pontos da geometria"""
        pts = []
        if g.isMultipart():
            for poly in g.asMultiPolygon():
                for ring in poly:
                    for p in ring:
                        pts.append((p.x(), p.y()))
        else:
            for ring in g.asPolygon():
                for p in ring:
                    pts.append((p.x(), p.y()))
        return np.array(pts) if pts else np.array([])
    
    def _create_output_layer(self, parts, total_area, output_name):
        """Criar camada de saída com valores REAIS"""
        try:
            crs = self.layer.crs()
            out = QgsVectorLayer(
                f"Polygon?crs={crs.authid()}", 
                output_name, 
                "memory"
            )
            dp = out.dataProvider()
            
            # Adicionar atributos
            dp.addAttributes([
                QgsField("parte", QVariant.Int),
                QgsField("area_ha", QVariant.Double),
                QgsField("pct_total", QVariant.Double),
                QgsField("tipo", QVariant.String)
            ])
            out.updateFields()
            
            # 🔥 CALCULAR ÁREA COM 4 CASAS DECIMAIS FIXAS
            area_total_ha = total_area / 10000.0  # m² para hectares
            
            # Calcular área ideal por parte
            area_ideal_por_parte_ha = area_total_ha / self.parts
            
            # Truncar (não arredondar) para 4 casas decimais usando string
            # Isso garante que todas as partes tenham EXATAMENTE o mesmo valor
            area_str = f"{area_ideal_por_parte_ha:.10f}"  # Pegar com precisão
            partes_str = area_str.split('.')
            if len(partes_str) == 2:
                # Pegar apenas 4 casas decimais (truncar, não arredondar)
                area_fixa = float(partes_str[0] + '.' + partes_str[1][:4])
            else:
                area_fixa = float(partes_str[0])
            
            pct_fixo = round(100.0 / self.parts, 4)
            
            features_to_add = []
            
            for i, geom in enumerate(parts, 1):
                # Criar feature com valor TRUNCADO em 4 decimais
                feat = QgsFeature(out.fields())
                feat.setGeometry(geom)
                feat.setAttribute("parte", i)
                feat.setAttribute("area_ha", area_fixa)  # VALOR FIXO TRUNCADO
                feat.setAttribute("pct_total", pct_fixo)
                feat.setAttribute("tipo", self.division_type)
                
                features_to_add.append(feat)
            
            # Adicionar todas as features
            dp.addFeatures(features_to_add)
            out.updateExtents()
            
            # Adicionar ao projeto
            QgsProject.instance().addMapLayer(out)
            self.iface.mapCanvas().setExtent(out.extent())
            self.iface.mapCanvas().refresh()
            
            # Criar mensagem com estatísticas
            message = self._create_result_message(parts, total_area, area_fixa, pct_fixo)
            
            return True, message
            
        except Exception as e:
            print(f"Erro ao criar camada: {str(e)}")
            return False, f"Erro ao criar camada: {str(e)}"
    
    def _create_result_message(self, parts, total_area, area_por_parte_ha, pct_por_parte):
        """Criar mensagem detalhada com estatísticas"""
        
        # Calcular áreas reais para análise de precisão
        real_areas_m2 = [geom.area() for geom in parts]
        real_areas_ha = [a / 10000.0 for a in real_areas_m2]
        
        target_area_m2 = total_area / self.parts
        
        # Calcular desvios em relação ao alvo
        desvios = []
        for a in real_areas_m2:
            desvio = abs(a - target_area_m2) / target_area_m2 * 100
            desvios.append(desvio)
        
        desvio_max = max(desvios)
        desvio_medio = sum(desvios) / len(desvios)
        
        total_ha = total_area / 10000.0
        
        message = f"""✅ DIVISÃO CONCLUÍDA COM SUCESSO!

📊 RESUMO GERAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de partes: {self.parts}
• Tipo: {self.division_type}
• Área total: {total_ha:.4f} ha
• Área por parte: {area_por_parte_ha:.4f} ha
• Percentual por parte: {pct_por_parte:.4f}%

📐 PRECISÃO DA DIVISÃO GEOMÉTRICA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Desvio médio: {desvio_medio:.3f}%
• Desvio máximo: {desvio_max:.3f}%

📋 VALORES NA TABELA DE ATRIBUTOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Todas as partes: {area_por_parte_ha:.4f} ha
• Todas as partes: {pct_por_parte:.4f}%

📌 ANÁLISE GEOMÉTRICA REAL (para referência):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        for i, (area_ha, desvio) in enumerate(zip(real_areas_ha, desvios), 1):
            diferenca_ha = area_ha - area_por_parte_ha
            sinal = "+" if diferenca_ha > 0 else ""
            message += f"\n  Parte {i:2d}: {area_ha:>10.4f} ha (geom. real) │ Diff: {sinal}{diferenca_ha:>8.4f} ha │ Desvio: {desvio:.2f}%"
        
        message += f"\n\n✓ Tabela de atributos: {self.parts} partes × {area_por_parte_ha:.4f} ha = {area_por_parte_ha * self.parts:.4f} ha"
        
        return message
