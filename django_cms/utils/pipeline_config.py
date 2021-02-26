PIPELINE_STYLESHEETS = {
    'novel': {
        'base': {
            'source_filenames': (
                'argon/assets/css/font-awesome.css',
                'argon/assets/css/argon-design-system.css',
                'scss/novel/base.scss',
                'scss/novel/includes/breadcrumb.scss',
                'scss/novel/includes/menu.scss',
                'scss/novel/includes/chapter_content.scss',
                'scss/novel/includes/novel_list.scss',
                'scss/novel/includes/chapter_list.scss',
                'scss/novel/includes/pagination.scss',
                'scss/novel/includes/novel_info.scss',
                'scss/novel/chapter.scss',
                'scss/novel/includes/footer.scss',
                'scss/novel/includes/link.scss',
                'scss/novel/includes/novel_cat.scss',
                'scss/novel/includes/base_auth_modal.scss',
                'scss/novel/includes/user_profile.scss',
                'scss/novel/includes/comment.scss',
            ),
            'output_filename': 'css/novel/base.css'
        },
        'style1': {
            'source_filenames': (
                'scss/style/style1.scss',
            ),
            'output_filename': 'css/novel/style1.css'
        },
    },
}

PIPELINE_JS = {
    'novel': {
        'base': {
            'source_filenames': (
                'js/novel/base.js',
                'js/novel/user.js',
                'js/novel/includes/base_auth_modal.js',
                'js/novel/includes/comment.js',
            ),
            'output_filename': 'js/novel/base.min.js'
        },
        'chapter': {
            'source_filenames': (
                'js/novel/chapter.js',
                'argon/assets/js/plugins/nouislider.min.js',
            ),
            'output_filename': 'js/novel/chapter.min.js'
        },
    },
}
