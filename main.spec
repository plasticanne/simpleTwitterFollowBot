# -*- mode: python ; coding: utf-8 -*-

import pathlib
pypylon_dir = pathlib.Path('./dlls')
pylon_dlls = [(str(dll), '.') for dll in pypylon_dir.glob('*.dll')]
block_cipher = None


a = Analysis(['main.py'],
             pathex=['D:\\py\\twitter\\twitter-bot'],
             binaries=pylon_dlls,
             datas=[('src/*','src/')],
             hiddenimports=[],
             hookspath=[],  
             runtime_hooks=[],
             excludes=[
                 'PyQt5',
                'sqlite3',
                'src.run'
                ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='twitterbot',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
            icon=''
           )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='twitterbot')
