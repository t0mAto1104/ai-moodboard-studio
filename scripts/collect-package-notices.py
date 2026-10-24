from importlib import metadata
from pathlib import Path
root=Path(__file__).resolve().parents[1]
parts=['AI Mood Board Studio — third-party software notices','No visual model weights are distributed in this package. Model licensing must accompany any separately obtained model.','Dependencies retain their own licenses. This file records installed build-runtime distribution license notices.','']
versions=[]
for distribution in sorted(metadata.distributions(),key=lambda d:d.metadata.get('Name','').lower()):
    name=distribution.metadata.get('Name','unknown');version=distribution.version
    versions.append(f'{name}=={version}')
    parts.extend(['\n'+'='*72,f'{name} {version}',distribution.metadata.get('License-Expression') or distribution.metadata.get('License') or 'See license texts below'])
    for entry in distribution.files or []:
        # Collect legal notices, not modules named packaging.licenses or bytecode.
        is_metadata=any(part.endswith(('.dist-info','.egg-info')) for part in entry.parts)
        is_notice=entry.name.lower() in ('license','license.txt','license.md','copying','notice','notice.txt') or entry.name.lower().startswith('license.')
        in_license_folder=is_metadata and any(part.lower()=='licenses' for part in entry.parts)
        if (is_notice or in_license_folder) and entry.suffix not in ('.py','.pyc','.so','.dylib'):
            file=distribution.locate_file(entry)
            if file.is_file() and file.stat().st_size<1_000_000:
                try:
                    value=file.read_text(encoding='utf-8')
                    if '\x00' not in value:parts.extend([str(entry),value])
                except (OSError,UnicodeError):pass
(root/'desktop/THIRD_PARTY_NOTICES.txt').write_text('\n'.join(parts)+'\n')
(root/'desktop/build-runtime-lock.txt').write_text('\n'.join(versions)+'\n')
