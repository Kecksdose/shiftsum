from setuptools import setup

setup(
    name='shiftsum',
    version='0.2dev0',
    packages=['shiftsummary'],
    license='MIT',
    long_description='Summarizes and plots lhcb DM/SL shifts.',
    entry_points = {
        'console_scripts': ['shiftsum=shiftsummary.command_line:main']
    },
    author='Timon Schmelzer',
    author_email='tisch1990@icloud.com',
    install_requires=[
        'pandas',
        'matplotlib'
    ],
    url='https://github.com/Kecksdose/ShiftAnalysis',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='lhcb shift datamanager shiftleader',
    python_requires='>=3.6'
)
