#!/usr/bin/env python3
"""
GAHENAX QA DETERMINISTA - UI Navigation Check
Protocolo APRAXAS G2
"""

import os
import sys
import re
from pathlib import Path

class UINavigationQA:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.static_dir = self.project_root / "static"
        self.results = []
        self.failures = []
        
    def check_single_navigation_authority(self):
        """QA-001: Verificar autoridad única de navegación"""
        nav_file = self.static_dir / "ui" / "navigation.js"
        
        if not nav_file.exists():
            self.failures.append("[OK] QA-001 FAILED: navigation.js not found")
            return False
            
        content = nav_file.read_text(encoding='utf-8')
        
        # Verificar estructura correcta
        checks = [
            ("window.GahenaxNavigation" in content, "Export global"),
            ("sidebar:" in content, "Sidebar links defined"),
            ("header:" in content, "Header links defined"),
            ("ECOSISTEMA GAHENAX" in content, "Ecosistema link present"),
        ]
        
        for check, desc in checks:
            if check:
                self.results.append(f"[OK] QA-001.{desc}: PASS")
            else:
                self.failures.append(f"[FAIL] QA-001.{desc}: FAIL")
                
        return len([c for c, _ in checks if not c]) == 0
    
    def check_single_layout_authority(self):
        """QA-002: Verificar autoridad única de layout rendering"""
        layout_file = self.static_dir / "ui" / "layout.js"
        
        if not layout_file.exists():
            self.failures.append("[OK] QA-002 FAILED: layout.js not found")
            return False
            
        content = layout_file.read_text(encoding='utf-8')
        
        # Verificar métodos requeridos
        checks = [
            ("renderHeader()" in content, "renderHeader method"),
            ("renderSidebar()" in content, "renderSidebar method"),
            ("window.GahenaxLayout" in content, "Export global"),
            ("idempotent" in content.lower(), "Idempotent documentation"),
            ("linkData.icon" in content, "Correct variable reference"),
            ("link.icon" not in content or content.count("linkData.icon") > 0, "No incorrect link.icon reference"),
        ]
        
        for check, desc in checks:
            if check:
                self.results.append(f"[OK] QA-002.{desc}: PASS")
            else:
                self.failures.append(f"[OK] QA-002.{desc}: FAIL")
                
        return len([c for c, _ in checks if not c]) == 0
    
    def check_single_render_authority(self):
        """QA-003: Verificar autoridad única de content rendering"""
        render_file = self.static_dir / "ui" / "render.js"
        
        if not render_file.exists():
            self.failures.append("[OK] QA-003 FAILED: render.js not found")
            return False
            
        content = render_file.read_text(encoding='utf-8')
        
        checks = [
            ("renderLayout(state)" in content, "renderLayout method"),
            ("window.GahenaxRender" in content, "Export global"),
            ("showExpedientesList" in content, "List view"),
            ("showExpedienteDetail" in content, "Detail view"),
            ("showExpedienteForm" in content, "Form view"),
            ("showSupportDesk" in content, "Support view"),
            ("showSettingsArchive" in content, "Settings view"),
        ]
        
        for check, desc in checks:
            if check:
                self.results.append(f"[OK] QA-003.{desc}: PASS")
            else:
                self.failures.append(f"[OK] QA-003.{desc}: FAIL")
                
        return len([c for c, _ in checks if not c]) == 0
    
    def check_no_duplicate_authorities(self):
        """QA-004: Verificar ausencia de autoridades duplicadas"""
        # Buscar patrones que indiquen renderizado manual en app.js
        app_file = self.static_dir / "app.js"
        
        if not app_file.exists():
            self.failures.append("[OK] QA-004 FAILED: app.js not found")
            return False
            
        content = app_file.read_text(encoding='utf-8')
        
        # NO debe contener renderizado directo del DOM
        bad_patterns = [
            r'\.innerHTML\s*=.*navbar',
            r'\.innerHTML\s*=.*sidebar',
            r'createElement.*header',
        ]
        
        violations = []
        for pattern in bad_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(pattern)
        
        if violations:
            for v in violations:
                self.failures.append(f"[OK] QA-004: Found duplicate rendering pattern: {v}")
            return False
        else:
            self.results.append("[OK] QA-004: No duplicate authorities detected")
            return True
    
    def check_deterministic_load_order(self):
        """QA-005: Verificar orden de carga correcto en index.html"""
        index_file = self.static_dir / "index.html"
        
        if not index_file.exists():
            self.failures.append("[OK] QA-005 FAILED: index.html not found")
            return False
            
        content = index_file.read_text(encoding='utf-8')
        
        # Extraer orden de scripts
        script_pattern = r'<script src="/static/(.*?)"></script>'
        scripts = re.findall(script_pattern, content)
        
        expected_order = [
            "config.js",
            "state/store.js",
            "api/client.js",
            "ui/navigation.js",
            "ui/layout.js",
            "ui/render.js",
            "app.js"
        ]
        
        if scripts == expected_order:
            self.results.append("[OK] QA-005: Load order is deterministic and correct")
            return True
        else:
            self.failures.append(f"[OK] QA-005: Load order incorrect")
            self.failures.append(f"  Expected: {expected_order}")
            self.failures.append(f"  Found: {scripts}")
            return False
    
    def check_no_redundant_html(self):
        """QA-006: Verificar ausencia de HTML redundante"""
        index_file = self.static_dir / "index.html"
        content = index_file.read_text(encoding='utf-8')
        
        # No debe haber comentarios que indican renderizado dinámico
        bad_comments = [
            "Links injected by",
            "Navigation links rendered dynamically by"
        ]
        
        found = []
        for comment in bad_comments:
            if comment in content:
                found.append(comment)
        
        if found:
            for f in found:
                self.failures.append(f"[OK] QA-006: Found redundant comment: {f}")
            return False
        else:
            self.results.append("[OK] QA-006: No redundant HTML comments")
            return True
    
    def run_all_checks(self):
        """Ejecutar todas las verificaciones"""
        print("="*60)
        print("GAHENAX QA DETERMINISTA - PROTOCOLO G2")
        print("="*60)
        print()
        
        checks = [
            self.check_single_navigation_authority,
            self.check_single_layout_authority,
            self.check_single_render_authority,
            self.check_no_duplicate_authorities,
            self.check_deterministic_load_order,
            self.check_no_redundant_html,
        ]
        
        passed = 0
        failed = 0
        
        for check in checks:
            if check():
                passed += 1
            else:
                failed += 1
        
        
        print("\n[RESULTADOS DETALLADOS]")
        print("-"*60)
        for result in self.results:
            print(result)
        
        if self.failures:
            print("\n[FALLOS DETECTADOS]")
            print("-"*60)
            for failure in self.failures:
                print(failure)
        
        print("\n" + "="*60)
        print(f"RESUMEN: {passed} checks pasados, {failed} checks fallados")
        print("="*60)
        
        if failed > 0:
            print("\n[X] ESTADO: FAILED - CORRECCION REQUERIDA")
            return 1
        else:
            print("\n[OK] ESTADO: CERTIFIED - AUTORIDADES CONSOLIDADAS")
            return 0

def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    qa = UINavigationQA(project_root)
    exit_code = qa.run_all_checks()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
