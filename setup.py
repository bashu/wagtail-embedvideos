#!/usr/bin/env python
from distutils.core import setup


setup(
    name='wagtail_embed_videos',
    version='0.3.0',
    description='Embed Videos for Wagtail CMS.',
    long_description=(
        "Simple app that works similar to wagtailimages,"
        "but for embedding YouTube and Vimeo videos and music from SoundCloud."
        "It's an integration of django-embed-video."
        ),
    author='InfoPortugal S.A.',
    author_email='suporte24@gmail.com',
    maintainer='InfoPortugal S.A.',
    maintainer_email='suporte24@gmail.com',
    url='https://github.com/infoportugal/wagtail-embedvideos',
    packages=[
        'wagtail_embed_videos',
        'wagtail_embed_videos.views',
        'wagtail_embed_videos.migrations'],
    package_data={
        'wagtail_embed_videos': [
            'static/wagtail_embed_videos/js/*.js',
            'templates/wagtail_embed_videos/chooser/*.html',
            'templates/wagtail_embed_videos/edit_handlers/*.html',
            'templates/wagtail_embed_videos/embed_videos/*.html',
            'templates/wagtail_embed_videos/widgets/*.html',
            'templates/wagtail_embed_videos/chooser/*.js',
            'templates/wagtail_embed_videos/edit_handlers/*.js',
            'templates/wagtail_embed_videos/embed_videos/*.js',
            'templates/wagtail_embed_videos/widgets/*.js'
        ]
    },
    install_requires=[
        'django>=1.7', 'wagtail>=1.6', 'django-embed-video>=1.0'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'],
    license='New BSD',

)
