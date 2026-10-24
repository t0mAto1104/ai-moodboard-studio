import numpy as np
from PIL import ImageColor
from skimage.color import rgb2lab,rgb2hsv,deltaE_ciede2000
from skimage.filters import laplace

def analyze(image,palette):
    a=np.asarray(image.resize((96,96)),dtype=np.float32)/255
    hsv=rgb2hsv(a);lab=rgb2lab(a)
    # Quantized dominant colors weighted by area; deterministic and low-memory.
    colors,counts=np.unique((a.reshape(-1,3)*7).astype(int),axis=0,return_counts=True)
    ids=np.argsort(-counts)[:6];rgb=(colors[ids]+.5)/8;weights=counts[ids]/counts[ids].sum()
    targets=np.array([ImageColor.getrgb(c) for c in palette],dtype=np.float32)/255
    dist=deltaE_ciede2000(rgb2lab(rgb[:,None,:]),rgb2lab(targets[None,:,:]))
    score=float(np.sum(np.exp(-dist.min(axis=1)/25)*weights))
    gray=a.mean(axis=2);blur=float(np.var(laplace(gray)));exposure=float(((gray<.025)|(gray>.975)).mean())
    resolution=min(1,min(image.size)/500)
    quality=.4*resolution+.35*min(1,blur/.015)+.25*(1-exposure)
    hist=np.histogram(hsv[:,:,0],bins=12,range=(0,1),weights=hsv[:,:,1])[0];hist=hist/max(hist.sum(),1e-6)
    return {'palette_score':score,'quality_score':quality,'composition_score':min(image.width/image.height,image.height/image.width)**.25,'brightness':float(hsv[:,:,2].mean()),'saturation':float(hsv[:,:,1].mean()),'hsv_histogram':hist.tolist(),'dominant_colors':['#%02x%02x%02x'%tuple((c*255).astype(int)) for c in rgb]}
