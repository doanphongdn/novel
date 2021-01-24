PIPELINE_STYLESHEETS = {
    'novel': {
        'base': {
            'source_filenames': (
                'argon/assets/css/argon-design-system.css',
                'argon/assets/css/font-awesome.css',
                'scss/novel/base.scss',
                'scss/novel/includes/breadcrumb.scss',
                'scss/novel/includes/navbar.scss',
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
            ),
            'output_filename': 'css/novel/base.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
    },
}
