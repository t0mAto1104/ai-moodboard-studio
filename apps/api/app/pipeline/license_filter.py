from app.schemas.models import ImageAsset
import time
class LicensePolicyEngine:
    def apply(self,a:ImageAsset,commercial=True):
        for key in ('allowed_display','allowed_temporary_analysis','allowed_store','allowed_transform','allowed_export'):setattr(a,key,False)
        a.copyright_review_status='unknown'
        a.display_url='';a.allowed_reference_board=False;a.allowed_download=False;a.download_reason='许可未核实，请到来源页面确认'
        from urllib.parse import urlparse
        hosts={'unsplash':{'images.unsplash.com'},'pixabay':{'cdn.pixabay.com','pixabay.com'},'openverse':{'api.openverse.org'},'artic':{'www.artic.edu'},'metmuseum':{'images.metmuseum.org'}}
        url=a.thumbnail_url or a.image_url
        parsed=urlparse(url)
        if parsed.scheme=='https' and parsed.hostname in hosts.get(a.provider,set()) and not parsed.username and not parsed.password and parsed.port in (None,443):
            a.display_url=url
        if a.provider in ('unsplash','pixabay') and a.display_url:
            a.allowed_reference_board=True
        download=urlparse(a.download_url)
        safe_download=download.scheme=='https' and download.hostname in hosts.get(a.provider,set()) and not download.username and not download.password and download.port in (None,443)
        if a.provider=='unsplash' and safe_download:
            event=urlparse(a.license_evidence.get('download_location') or '')
            if event.scheme=='https' and event.hostname=='api.unsplash.com' and event.path=='/photos/'+a.provider_asset_id+'/download' and not event.username and not event.password and event.port in (None,443):
                a.allowed_download=True;a.download_reason='单张手动下载；需上报 Unsplash 下载事件'
        if a.provider=='pixabay' and safe_download and a.license_type=='Pixabay Content License':
            a.allowed_download=True;a.download_reason='单张手动下载；后续使用遵守 Pixabay Content License'
        # Only provenance gathered from a trusted adapter is a source verification.
        verified=a.license_evidence.get('source_verified') is True and a.provider in ('artic','metmuseum','mock','upload')
        a.allowed_display = a.provider in ('openverse','unsplash','pixabay') or verified
        # Official stock licenses permit derivative boards. This is independent
        # from ML analysis permission and from persistent image-file storage.
        source=urlparse(a.source_page_url)
        official_source=source.scheme=='https' and not source.username and not source.password and source.port in (None,443)
        licensed=(a.provider=='unsplash' and a.license_type in ('Unsplash License','Unsplash API research-only') and source.hostname=='unsplash.com') or (a.provider=='pixabay' and a.license_type=='Pixabay Content License' and source.hostname=='pixabay.com')
        if official_source and licensed and a.display_url and a.attribution_text:
            a.license_verified_at=time.time();a.copyright_review_status='verified_source_license'
            a.allowed_transform=a.allowed_export=True
            a.allowed_store=a.provider=='pixabay'
            a.license_type='Unsplash License' if a.provider=='unsplash' else a.license_type
            a.license_url='https://unsplash.com/license' if a.provider=='unsplash' else 'https://pixabay.com/service/terms/'
            a.license_evidence={**a.license_evidence,'source_verified':True,'export_basis':'official-stock-license-v1','export_scope':'creative mood board; source restrictions and third-party rights still apply'}
            a.license_evidence.pop('reason',None)
        if a.provider=='unsplash' and a.display_url:
            from app.db import store
            cfg=store.get('settings','provider:unsplash') or {}
            evidence=cfg.get('analysis_authorization') or {}
            if cfg.get('analysis_enabled') and evidence.get('rights_confirmed') and evidence.get('scope')=='local_inference_only':
                a.allowed_temporary_analysis=True
                a.copyright_review_status='user_authorized_analysis'
                a.license_evidence={**a.license_evidence,'analysis_authorization':evidence}
        if not verified:return a
        a.license_verified_at=time.time(); a.copyright_review_status='verified'
        lic=a.license_type.lower()
        allowed=lic in ('cc0','pdm','public domain','cc by','user-owned') or (lic=='cc by-nc' and not commercial)
        if allowed:
            a.allowed_temporary_analysis=a.allowed_store=a.allowed_transform=True
            a.allowed_export=bool(a.attribution_text) if lic.startswith('cc by') else True
        if allowed and a.allowed_export:
            a.allowed_download=True;a.download_reason='来源许可允许下载'
        return a
    def require_export(self,a,commercial=True):
        a=self.apply(a,commercial)
        if not all((a.allowed_transform,a.allowed_export)):
            raise ValueError(f'素材 {a.id} 的许可不允许导出，请替换。')
        return a
policy=LicensePolicyEngine()
