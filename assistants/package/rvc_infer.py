import os,sys,pdb,torch
now_dir = os.getcwd()
sys.path.append(now_dir)
import argparse
import glob
import sys
import torch
import numpy as np
import yaml
import pkg_resources

from multiprocessing import cpu_count
from vc_infer_pipeline import VC
from lib.infer_pack.models import SynthesizerTrnMs256NSFsid, SynthesizerTrnMs256NSFsid_nono, SynthesizerTrnMs768NSFsid, SynthesizerTrnMs768NSFsid_nono
from my_utils import load_audio
from .assistant_utils import create_directory, get_path

from fairseq import checkpoint_utils
from scipy.io import wavfile


class Config:
    def __init__(self,device,is_half):
        self.device = device
        self.is_half = is_half
        self.n_cpu = 0
        self.gpu_name = None
        self.gpu_mem = None
        self.x_pad, self.x_query, self.x_center, self.x_max = self.device_config()

    def device_config(self) -> tuple:
        if torch.cuda.is_available():
            i_device = int(self.device.split(":")[-1])
            self.gpu_name = torch.cuda.get_device_name(i_device)
            if (
                ("16" in self.gpu_name and "V100" not in self.gpu_name.upper())
                or "P40" in self.gpu_name.upper()
                or "1060" in self.gpu_name
                or "1070" in self.gpu_name
                or "1080" in self.gpu_name
            ):
                print("16系/10系显卡和P40强制单精度")
                self.is_half = False
                for config_file in ["32k.json", "40k.json", "48k.json"]:
                    with open(f"configs/{config_file}", "r") as f:
                        strr = f.read().replace("true", "false")
                    with open(f"configs/{config_file}", "w") as f:
                        f.write(strr)
                with open("trainset_preprocess_pipeline_print.py", "r") as f:
                    strr = f.read().replace("3.7", "3.0")
                with open("trainset_preprocess_pipeline_print.py", "w") as f:
                    f.write(strr)
            else:
                self.gpu_name = None
            self.gpu_mem = int(
                torch.cuda.get_device_properties(i_device).total_memory
                / 1024
                / 1024
                / 1024
                + 0.4
            )
            if self.gpu_mem <= 4:
                with open("trainset_preprocess_pipeline_print.py", "r") as f:
                    strr = f.read().replace("3.7", "3.0")
                with open("trainset_preprocess_pipeline_print.py", "w") as f:
                    f.write(strr)
        elif torch.backends.mps.is_available():
            print("没有发现支持的N卡, 使用MPS进行推理")
            self.device = "mps"
        else:
            print("没有发现支持的N卡, 使用CPU进行推理")
            self.device = "cpu"
            self.is_half = True

        if self.n_cpu == 0:
            self.n_cpu = cpu_count()

        if self.is_half:
            # 6G显存配置
            x_pad = 3
            x_query = 10
            x_center = 60
            x_max = 65
        else:
            # 5G显存配置
            x_pad = 1
            x_query = 6
            x_center = 38
            x_max = 41

        if self.gpu_mem != None and self.gpu_mem <= 4:
            x_pad = 1
            x_query = 5
            x_center = 30
            x_max = 32

        return x_pad, x_query, x_center, x_max
    
def load_hubert():
    global hubert_model
    file_path = "assistants\\package\\rvc\\hubert_base.pt"
    models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
        [file_path],
        suffix="",
    )
    hubert_model = models[0]
    hubert_model = hubert_model.to(config.device)
    if config.is_half:
        hubert_model = hubert_model.half()
    else:
        hubert_model = hubert_model.float()
    hubert_model.eval()

def vc_single(
    sid,
    input_audio_path,
    f0_up_key,
    f0_file,
    f0_method,
    file_index,
    file_index2,
    # file_big_npy,
    index_rate,
    filter_radius,
    resample_sr,
    rms_mix_rate,
    protect,
):  # spk_item, input_audio0, vc_transform0,f0_file,f0method0
    global tgt_sr, net_g, vc, hubert_model, version
    f0_file = None
    if input_audio_path is None:
        return "You need to upload an audio", None
    f0_up_key = int(f0_up_key)
    audio = load_audio(input_audio_path, 16000)
    audio_max = np.abs(audio).max() / 0.95
    if audio_max > 1:
        audio /= audio_max
    times = [0, 0, 0]
    if not hubert_model:
        load_hubert()
    if_f0 = cpt.get("f0", 1)
    file_index = (
        (
            file_index.strip(" ")
            .strip('"')
            .strip("\n")
            .strip('"')
            .strip(" ")
            .replace("trained", "added")
        )
        if file_index != ""
        else file_index2
    )  # 防止小白写错，自动帮他替换掉
    # file_big_npy = (
    #     file_big_npy.strip(" ").strip('"').strip("\n").strip('"').strip(" ")
    # )
    audio_opt = vc.pipeline(
        hubert_model,
        net_g,
        sid,
        audio,
        input_audio_path,
        times,
        f0_up_key,
        f0_method,
        file_index,
        # file_big_npy,
        index_rate,
        if_f0,
        filter_radius,
        tgt_sr,
        resample_sr,
        rms_mix_rate,
        version,
        protect,
        f0_file=f0_file,
    )
    return audio_opt

def get_vc(model_path):
    global n_spk,tgt_sr,net_g,vc,cpt,device,is_half, version
    print("loading pth %s"%model_path)
    cpt = torch.load(model_path, map_location="cpu")
    tgt_sr = cpt["config"][-1]
    cpt["config"][-3]=cpt["weight"]["emb_g.weight"].shape[0]#n_spk
    if_f0=cpt.get("f0",1)
    version = cpt.get("version", "v1")
    if version == "v1":
        if if_f0 == 1:
            net_g = SynthesizerTrnMs256NSFsid(
                *cpt["config"], is_half=config.is_half
            )
        else:
            net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
    elif version == "v2":
        if if_f0 == 1:
            net_g = SynthesizerTrnMs768NSFsid(
                *cpt["config"], is_half=config.is_half
            )
        else:
            net_g = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
    del net_g.enc_q
    print(net_g.load_state_dict(cpt["weight"], strict=False))
    net_g.eval().to(device)
    if (is_half):net_g = net_g.half()
    else:net_g = net_g.float()
    vc = VC(tgt_sr, config)
    n_spk=cpt["config"][-3]
    # return {"visible": True,"maximum": n_spk, "__type__": "update"}

def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_file = os.path.join(current_dir, "rvc.yaml")

    with open(yaml_file, "r") as file:
        rvc_conf = yaml.safe_load(file)

    return rvc_conf

def rvc_run(input_path, output_dir):
    global config, now_dir, hubert_model, tgt_sr, net_g, vc, cpt, device, is_half, version

    settings = load_config()

    f0_up_key = settings["transpose"]
    # input_path = settings["audio_file"]
    # output_dir = settings["output_file"]
    model_path = get_path(settings["model_path"])
    device = settings["device"]
    is_half = settings["is_half"]
    f0method = settings["f0method"]
    file_index = settings["file_index"]
    file_index2 = settings["file_index2"]
    index_rate = settings["index_rate"]
    filter_radius = settings["filter_radius"]
    resample_sr = settings["resample_sr"]
    rms_mix_rate = settings["rms_mix_rate"]
    protect = settings["protect"]
    print(settings)

    if(is_half.lower() == 'true'):
        is_half = True
    else:
        is_half = False

    config=Config(device,is_half)
    now_dir=os.getcwd()
    sys.path.append(now_dir)


    hubert_model=None


    get_vc(model_path)
    wav_opt=vc_single(0,input_path,f0_up_key,None,f0method,file_index,file_index2,index_rate,filter_radius,resample_sr,rms_mix_rate,protect)
    wavfile.write(output_dir, tgt_sr, wav_opt)
    print(output_dir)
    print("File finished writing")



output_dir_name = "output"
create_directory(output_dir_name)
output_dir = get_path(output_dir_name)
output_file_name = "test.wav"
output_file_path = os.path.join(output_dir,output_file_name)

def main():
    # Need to comment out yaml setting for input audio
    rvc_run(output_file_path)

if __name__ == "__main__":
    main()