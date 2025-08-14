# gym_management/__manifest__.py
{
    'name': 'Gym Management',
    'version': '18.0.1.0.0',
    'summary': 'Manages Gyms, Companies, Reviews, and Galleries for a mobile app.',
    'author': 'Anda',
    'website': '',
    'category': 'Services/Gym',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/location_data.xml',
        'views/location_views.xml',
        'views/package_views.xml',
        'views/gym_views.xml',
        'views/user_views.xml',
        'views/register_views.xml',
        'views/menuitem.xml',
        'data/sequences.xml',
        'report/membership_report.xml',
        
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    #         'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    #         'gymnest_management/static/src/js/map_widget.js',
    #         'gymnest_management/static/src/xml/map_widget.xml',
    #     ],
    # },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}