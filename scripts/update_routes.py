#!/usr/bin/env python3
"""
Route Update Script for MiraiWorks Frontend
This script helps replace hardcoded routes with centralized ROUTES constants
"""

import os
import re
from pathlib import Path

# Route mappings from hardcoded strings to ROUTES constants
ROUTE_MAPPINGS = {
    # Users routes
    r'"/users"': 'ROUTES.USERS.BASE',
    r"'/users'": 'ROUTES.USERS.BASE',
    r'"/users/add"': 'ROUTES.USERS.ADD',
    r"'/users/add'": 'ROUTES.USERS.ADD',
    r'`/users/\$\{([^}]+)\}/edit`': r'ROUTES.USERS.EDIT(\1)',

    # Companies routes
    r'"/companies"': 'ROUTES.COMPANIES.BASE',
    r"'/companies'": 'ROUTES.COMPANIES.BASE',
    r'"/companies/add"': 'ROUTES.COMPANIES.ADD',
    r"'/companies/add'": 'ROUTES.COMPANIES.ADD',
    r'`/companies/\$\{([^}]+)\}/edit`': r'ROUTES.COMPANIES.EDIT(\1)',

    # Candidates routes
    r'"/candidates"': 'ROUTES.CANDIDATES.BASE',
    r"'/candidates'": 'ROUTES.CANDIDATES.BASE',

    # Exams routes
    r'"/exams"': 'ROUTES.EXAMS.BASE',
    r"'/exams'": 'ROUTES.EXAMS.BASE',
    r'"/exams/demo"': 'ROUTES.EXAMS.DEMO.BASE',
    r"'/exams/demo'": 'ROUTES.EXAMS.DEMO.BASE',
    r'`/exams/take/\$\{([^}]+)\}`': r'ROUTES.EXAMS.TAKE(\1)',
    r'`/exams/results/\$\{([^}]+)\}`': r'ROUTES.EXAMS.RESULTS(\1)',

    # Admin Exams routes
    r'"/admin/exams"': 'ROUTES.ADMIN.EXAMS.BASE',
    r"'/admin/exams'": 'ROUTES.ADMIN.EXAMS.BASE',
    r'"/admin/exams/create"': 'ROUTES.ADMIN.EXAMS.CREATE',
    r"'/admin/exams/create'": 'ROUTES.ADMIN.EXAMS.CREATE',
    r'`/admin/exams/\$\{([^}]+)\}/edit`': r'ROUTES.ADMIN.EXAMS.EDIT(\1)',
    r'`/admin/exams/\$\{([^}]+)\}/analytics`': r'ROUTES.ADMIN.EXAMS.ANALYTICS(\1)',
    r'`/admin/exams/\$\{([^}]+)\}/assign`': r'ROUTES.ADMIN.EXAMS.ASSIGN(\1)',
    r'`/admin/exams/\$\{([^}]+)\}/preview`': r'ROUTES.ADMIN.EXAMS.PREVIEW(\1)',
    r'`/admin/exams/\$\{([^}]+)\}/statistics`': r'ROUTES.ADMIN.EXAMS.STATISTICS(\1)',
    r'`/admin/exams/sessions/\$\{([^}]+)\}`': r'ROUTES.ADMIN.EXAMS.SESSION(\1)',
    r'"/admin/exams/templates"': 'ROUTES.ADMIN.EXAMS.TEMPLATES.BASE',
    r"'/admin/exams/templates'": 'ROUTES.ADMIN.EXAMS.TEMPLATES.BASE',

    # Admin Question Banks
    r'"/admin/question-banks"': 'ROUTES.ADMIN.QUESTION_BANKS.BASE',
    r"'/admin/question-banks'": 'ROUTES.ADMIN.QUESTION_BANKS.BASE',
    r'"/admin/question-banks/create"': 'ROUTES.ADMIN.QUESTION_BANKS.CREATE',
    r"'/admin/question-banks/create'": 'ROUTES.ADMIN.QUESTION_BANKS.CREATE',
    r'`/admin/question-banks/\$\{([^}]+)\}`': r'ROUTES.ADMIN.QUESTION_BANKS.BY_ID(\1)',

    # Interviews routes
    r'"/interviews"': 'ROUTES.INTERVIEWS.BASE',
    r"'/interviews'": 'ROUTES.INTERVIEWS.BASE',
    r'"/interviews/new"': 'ROUTES.INTERVIEWS.NEW',
    r"'/interviews/new'": 'ROUTES.INTERVIEWS.NEW',
    r'`/interviews/\$\{([^}]+)\}`': r'ROUTES.INTERVIEWS.BY_ID(\1)',
    r'`/interviews/\$\{([^}]+)\}/edit`': r'ROUTES.INTERVIEWS.EDIT(\1)',

    # Resumes routes
    r'"/resumes"': 'ROUTES.RESUMES.BASE',
    r"'/resumes'": 'ROUTES.RESUMES.BASE',
    r'"/resumes/create"': 'ROUTES.RESUMES.CREATE',
    r"'/resumes/create'": 'ROUTES.RESUMES.CREATE',
    r'"/resumes/builder"': 'ROUTES.RESUMES.BUILDER',
    r"'/resumes/builder'": 'ROUTES.RESUMES.BUILDER',
    r'`/resumes/\$\{([^}]+)\}/edit`': r'ROUTES.RESUMES.EDIT(\1)',
    r'`/resumes/\$\{([^}]+)\}/preview`': r'ROUTES.RESUMES.PREVIEW.BY_ID(\1)',
    r'"/resumes/preview"': 'ROUTES.RESUMES.PREVIEW.BASE',
    r"'/resumes/preview'": 'ROUTES.RESUMES.PREVIEW.BASE',

    # Room routes
    r'`/room/\$\{([^}]+)\}`': r'ROUTES.ROOM.BY_CODE(\1)',
}


def should_add_import(content: str) -> bool:
    """Check if ROUTES import should be added"""
    return 'import { ROUTES }' not in content and "from '@/routes/config'" not in content


def add_routes_import(content: str) -> str:
    """Add ROUTES import to the file"""
    if should_add_import(content):
        # Find the last import statement
        import_pattern = r"(import\s+.*?;)"
        imports = list(re.finditer(import_pattern, content, re.MULTILINE))

        if imports:
            last_import = imports[-1]
            insert_pos = last_import.end()
            # Add the new import after the last import
            new_import = "\nimport { ROUTES } from '@/routes/config';"
            content = content[:insert_pos] + new_import + content[insert_pos:]

    return content


def replace_routes(content: str) -> tuple[str, int]:
    """Replace hardcoded routes with ROUTES constants"""
    replacements = 0

    for pattern, replacement in ROUTE_MAPPINGS.items():
        matches = list(re.finditer(pattern, content))
        if matches:
            content = re.sub(pattern, replacement, content)
            replacements += len(matches)

    return content, replacements


def process_file(file_path: Path) -> dict:
    """Process a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace routes
        content, replacements = replace_routes(content)

        # Add import if needed and replacements were made
        if replacements > 0:
            content = add_routes_import(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'file': str(file_path),
                'replacements': replacements,
                'success': True
            }

        return {
            'file': str(file_path),
            'replacements': 0,
            'success': True,
            'message': 'No changes needed'
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'replacements': 0,
            'success': False,
            'error': str(e)
        }


def main():
    """Main function"""
    base_dir = Path(__file__).parent.parent / 'frontend' / 'src' / 'app' / '[locale]' / '(app)'

    # Find all TypeScript/TSX files
    files_to_process = list(base_dir.rglob('*.tsx')) + list(base_dir.rglob('*.ts'))

    results = []
    total_replacements = 0

    print(f"Processing {len(files_to_process)} files...")
    print("-" * 80)

    for file_path in files_to_process:
        result = process_file(file_path)
        results.append(result)

        if result.get('replacements', 0) > 0:
            total_replacements += result['replacements']
            print(f"✓ {file_path.relative_to(base_dir)}: {result['replacements']} replacements")
        elif not result['success']:
            print(f"✗ {file_path.relative_to(base_dir)}: ERROR - {result.get('error')}")

    print("-" * 80)
    print(f"\nSummary:")
    print(f"  Files processed: {len(results)}")
    print(f"  Files modified: {sum(1 for r in results if r.get('replacements', 0) > 0)}")
    print(f"  Total replacements: {total_replacements}")
    print(f"  Errors: {sum(1 for r in results if not r['success'])}")


if __name__ == '__main__':
    main()
