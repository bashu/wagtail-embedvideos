from setuptools import setup, find_packages


setup(
    name='wagtail_embed_videos',
    version='0.3.0',
    description='Embed Videos for Wagtail CMS.',
    long_description=(
        "Simple app that works similar to wagtailimages,"
        "but for embedding YouTube and Vimeo videos and music from SoundCloud."
        "It's an integration of django-embed-video."
        ),
    author='Diogo Marques',
    author_email='doriva.marques.29@gmail.com',
    maintainer='Diogo Marques',
    maintainer_email='doriva.marques.29@gmail.com',
    url='https://github.com/infoportugal/wagtail-embedvideos',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.7', 'wagtail>=1.0', 'django-embed-video>=1.0'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'],
    license='New BSD',

)

