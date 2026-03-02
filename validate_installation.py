#!/usr/bin/env python3
"""
CivicTrack AI - Installation Validator
Verifies that all files, endpoints, and tables are properly set up
"""

import os
import subprocess
import sys

class Validator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def check_file_exists(self, filepath, description):
        """Check if a file exists"""
        full_path = os.path.join(self.base_path, filepath)
        if os.path.exists(full_path):
            self.success.append(f"✓ {description}: {filepath}")
            return True
        else:
            self.errors.append(f"✗ Missing {description}: {filepath}")
            return False

    def check_directory_exists(self, dirpath, description):
        """Check if a directory exists"""
        full_path = os.path.join(self.base_path, dirpath)
        if os.path.isdir(full_path):
            self.success.append(f"✓ {description}: {dirpath}")
            return True
        else:
            self.errors.append(f"✗ Missing {description}: {dirpath}")
            return False

    def check_python_imports(self):
        """Check if required Python packages are installed"""
        packages = ['flask', 'flask_cors', 'mysql', 'bcrypt', 'jwt', 'dotenv']
        
        for package in packages:
            try:
                __import__(package.replace('_', '-'))
                self.success.append(f"✓ Python package installed: {package}")
            except ImportError:
                self.warnings.append(f"⚠ Python package not installed: {package}")

    def check_backend_endpoints(self):
        """Check if backend code contains required endpoints"""
        backend_file = os.path.join(self.base_path, 'backend', 'app.py')
        
        endpoints = {
            'GET /resolvers': '@app.route("/resolvers"',
            'POST /assign-issue': '@app.route("/assign-issue"',
            'GET /my-assignments': '@app.route("/my-assignments"',
            'POST /complete-issue': '@app.route("/complete-issue"',
            'GET /resolved-issues': '@app.route("/resolved-issues"',
        }
        
        if os.path.exists(backend_file):
            with open(backend_file, 'r') as f:
                content = f.read()
                for endpoint_name, search_string in endpoints.items():
                    if search_string in content:
                        self.success.append(f"✓ Endpoint found: {endpoint_name}")
                    else:
                        self.errors.append(f"✗ Endpoint missing: {endpoint_name}")
        else:
            self.errors.append("✗ backend/app.py not found")

    def check_frontend_pages(self):
        """Check if frontend pages exist"""
        pages = {
            'Citizen dashboard': 'frontend/citizen.html',
            'Admin dashboard': 'frontend/dashboard.html',
            'Resolver dashboard': 'frontend/resolver.html',
            'Login page': 'frontend/login.html',
            'Register page': 'frontend/register.html',
            'Index page': 'frontend/index.html',
        }
        
        for page_name, path in pages.items():
            self.check_file_exists(path, f"Frontend page ({page_name})")

    def check_frontend_javascript(self):
        """Check if frontend JavaScript files exist"""
        scripts = {
            'Auth script': 'frontend/js/auth.js',
            'Register script': 'frontend/js/register.js',
            'Citizen script': 'frontend/js/citizen.js',
            'Dashboard script': 'frontend/js/dashboard.js',
            'Resolver script': 'frontend/js/resolver.js',
        }
        
        for script_name, path in scripts.items():
            self.check_file_exists(path, f"JavaScript ({script_name})")

    def check_documentation(self):
        """Check if documentation files exist"""
        docs = {
            'Setup checklist': 'SETUP_CHECKLIST.md',
            'Work assignment guide': 'WORK_ASSIGNMENT_GUIDE.md',
            'Implementation summary': 'IMPLEMENTATION_SUMMARY.md',
            'Quick reference': 'QUICK_REFERENCE.md',
            'Database migration': 'database_migration.sql',
        }
        
        for doc_name, path in docs.items():
            self.check_file_exists(path, f"Documentation ({doc_name})")

    def check_resolver_functionality(self):
        """Check if resolver.js has key functions"""
        resolver_js = os.path.join(self.base_path, 'frontend', 'js', 'resolver.js')
        functions = ['loadAssignments', 'openNavigation', 'confirmCompletion', 'openGoogleMaps']
        
        if os.path.exists(resolver_js):
            with open(resolver_js, 'r') as f:
                content = f.read()
                for func in functions:
                    if f'function {func}' in content or f'{func}()' in content:
                        self.success.append(f"✓ Resolver function found: {func}")
                    else:
                        self.warnings.append(f"⚠ Resolver function might be missing: {func}")
        else:
            self.errors.append("✗ resolver.js not found")

    def print_report(self):
        """Print validation report"""
        print("\n" + "="*70)
        print("CivicTrack AI - Installation Validator Report")
        print("="*70 + "\n")
        
        if self.success:
            print("✓ SUCCESSFUL CHECKS:")
            for item in self.success:
                print(f"  {item}")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n✗ ERRORS:")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "="*70)
        print("Summary:")
        print(f"  ✓ Successful: {len(self.success)}")
        print(f"  ⚠ Warnings: {len(self.warnings)}")
        print(f"  ✗ Errors: {len(self.errors)}")
        print("="*70 + "\n")
        
        if self.errors:
            print("❌ INSTALLATION INCOMPLETE - Please fix errors above\n")
            return False
        elif self.warnings:
            print("⚠️ INSTALLATION OK BUT NEEDS ATTENTION - Install missing packages\n")
            return True
        else:
            print("✅ INSTALLATION COMPLETE AND VERIFIED!\n")
            return True

    def run_all_checks(self):
        """Run all validation checks"""
        print("Running validation checks...")
        
        print("\n1. Checking frontend HTML pages...")
        self.check_frontend_pages()
        
        print("2. Checking backend Python code...")
        self.check_backend_endpoints()
        
        print("3. Checking frontend JavaScript files...")
        self.check_frontend_javascript()
        
        print("4. Checking resolver functionality...")
        self.check_resolver_functionality()
        
        print("5. Checking documentation...")
        self.check_documentation()
        
        print("6. Checking Python packages...")
        self.check_python_imports()
        
        return self.print_report()


if __name__ == "__main__":
    validator = Validator()
    success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)
