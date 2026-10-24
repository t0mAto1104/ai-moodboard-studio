import keyring
from app.core.config import DESKTOP
SERVICE='AI Mood Board Studio Desktop' if DESKTOP else 'AI Mood Board Studio'
class CredentialManager:
    def get(self,name):
        try:return keyring.get_password(SERVICE,name)
        except Exception:return None
    def save(self,name,value):
        # Refuse insecure fallback keyrings rather than silently writing plaintext.
        backend=keyring.get_keyring()
        if not backend.__class__.__module__.startswith(('keyring.backends.macOS','keyring.backends.SecretService','keyring.backends.Windows')):
            raise ValueError('系统安全凭证存储不可用；密钥未保存')
        try:
            if value:keyring.set_password(SERVICE,name,value)
            else:keyring.delete_password(SERVICE,name)
        except keyring.errors.PasswordDeleteError:pass
        except Exception:raise ValueError('系统钥匙串操作失败；请检查访问权限')
credentials=CredentialManager()
