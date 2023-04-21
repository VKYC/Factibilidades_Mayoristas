{
    'name': 'Widget maps',
    'version': '1.0',
    'description': '',
    'summary': '',
    'author': 'Jhon Jairo Rojas Ortiz',
    'website': '',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'web', 'base_setup'
    ],
    'data': [
        'views/res_config_settings.xml',
        'views/widget_maps_template.xml'
    ],
    'demo': [
        
    ],
    'auto_install': True,
    'application': False,
    'assets': {
        'web.assets_backend': [
    '/widget_maps/static/src/css/widget_maps.css',
    '/widget_maps/static/src/js/widget_maps.js',
        ],
        'web.assets_qweb': [
            '/widget_maps/static/src/xml/**/*',
        ],
    }
}