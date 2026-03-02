import gdown
if __name__ == "__main__":
    cnh_url = "link do arquivo google drive"
    gdown.download(cnh_url, "samples/cnh.pdf", quiet=False)
    
    selfie_url = "link do arquivo google drive"
    gdown.download(selfie_url, "samples/selfie.jpg", quiet=False)
    

