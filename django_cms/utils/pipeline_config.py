PIPELINE_STYLESHEETS = {
    'novel': {
        'base': {
            'source_filenames': (
                'argon/assets/css/font-awesome.css',
                'argon/assets/css/argon-design-system.css',
                'scss/novel/base.scss',
                'scss/novel/chapter.scss',
                'scss/novel/novel_all.scss',
                'scss/novel/includes/breadcrumb.scss',
                'scss/novel/includes/menu.scss',
                'scss/novel/includes/chapter_content.scss',
                'scss/novel/includes/novel_list.scss',
                'scss/novel/includes/chapter_list.scss',
                'scss/novel/includes/pagination.scss',
                'scss/novel/includes/novel_info.scss',
                'scss/novel/includes/footer.scss',
                'scss/novel/includes/link.scss',
                'scss/novel/includes/novel_cat.scss',
                'scss/novel/includes/base_auth_modal.scss',
                'scss/novel/includes/user_profile.scss',
                'scss/novel/includes/comment.scss',
                'scss/novel/includes/sidebar.scss',
            ),
            'output_filename': 'css/novel/base.css'
        },
        'style1': {
            'source_filenames': (
                'scss/style/style1.scss',
            ),
            'output_filename': 'css/novel/style1.css'
        },
        'style2': {
            'source_filenames': (
                'scss/style/style2.scss',
            ),
            'output_filename': 'css/novel/style2.css'
        },
    },
}

PIPELINE_JS = {
    'novel': {
        'base': {
            'source_filenames': (
                'js/novel/base.js',
                'js/novel/includes/base_auth_modal.js',
            ),
            'output_filename': 'js/novel/base.min.js'
        },
        'user': {
            'source_filenames': (
                'js/novel/user.js',
            ),
            'output_filename': 'js/novel/user.min.js'
        },
        'novel': {
            'source_filenames': (
                'js/novel/includes/comment.js',
                'js/novel/includes/report_modal.js',
                'js/novel/novel.js',
            ),
            'output_filename': 'js/novel/novel.min.js'
        },
        'chapter': {
            'source_filenames': (
                'js/novel/includes/report_modal.js',
                'js/novel/includes/comment.js',
                'js/novel/chapter.js',
            ),
            'output_filename': 'js/novel/chapter.min.js'
        },
    },
}
