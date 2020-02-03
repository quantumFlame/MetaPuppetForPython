from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(name='MetaPuppet',
          version=1.0,
          author="God Player Group",
          author_email="godplayergroup@gmail.com",
          license="MIT License",
          packages=find_packages(),
          install_requires=[
              'python-socketio',
              'sanic',
              'regex',
          ],
          zip_safe=False)
