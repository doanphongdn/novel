PIPELINE_STYLESHEETS = {
    'novel': {
        'base': {
            'source_filenames': (
                'argon/assets/css/argon-design-system.css',
                'argon/assets/css/font-awesome.css',
                'scss/novel/base.scss',
                'scss/novel/widgets/breadcrumb.scss',
                'scss/novel/includes/chapter_content.scss',
                'scss/novel/includes/novel_grid.scss',
                'scss/novel/chapter.scss',
            ),
            'output_filename': 'css/novel/base.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
    },
}
