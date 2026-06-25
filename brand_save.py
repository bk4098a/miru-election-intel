import matplotlib
matplotlib.use("Agg")

import os
import glob
from pathlib import Path
from itertools import cycle, islice

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cycler
from matplotlib import font_manager as fm
from matplotlib.font_manager import FontProperties

# =========================================================
# 0) 출력 폴더
# =========================================================
def set_outdir(path: str):
    global outdir
    outdir = Path(path)
    outdir.mkdir(parents=True, exist_ok=True)

set_outdir("C:/Users/KIM/Downloads/miru_charts")   # 윈도우면 r"C:/Users/KIM/Downloads/miru_charts" 등으로 변경


# =========================================================
# 1) 폰트: Gmarket Sans
# =========================================================
def use_gmarket_sans_font(
    font_dir="C:/Users/KIM/Downloads/GmarketSansTTF",   # 윈도우면 r"C:/Users/KIM/Downloads/GmarketSansTTF"
    fallbacks=("Malgun Gothic", "Noto Sans CJK KR", "AppleGothic", "DejaVu Sans"),
):
    added = []
    if font_dir and os.path.isdir(font_dir):
        for p in glob.glob(os.path.join(font_dir, "*.ttf")) + glob.glob(os.path.join(font_dir, "*.TTF")):
            try:
                fm.fontManager.addfont(p); added.append(p)
            except Exception:
                pass

    preferred_order = ["Medium", "Bold", "Light"]
    chosen_name = None

    def _pick(keyword):
        for c in [p for p in added if keyword.lower() in os.path.basename(p).lower()]:
            try: return FontProperties(fname=c).get_name()
            except Exception: continue
        return None

    if added:
        for pref in preferred_order:
            chosen_name = _pick(pref)
            if chosen_name: break
        if not chosen_name:
            try: chosen_name = FontProperties(fname=added[0]).get_name()
            except Exception: chosen_name = None

    fams = ([chosen_name] if chosen_name else []) + list(fallbacks)
    if fams:
        mpl.rcParams["font.family"] = fams[0]
        mpl.rcParams["font.sans-serif"] = fams
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["svg.fonttype"] = "none"
    return chosen_name

use_gmarket_sans_font()


# =========================================================
# 2) THEME: MIRU Brand (네이비 + 레드)
# =========================================================
def set_miru_theme(mode: str = "light"):
    """miru_deck.js 디자인 토큰과 동일한 팔레트."""
    is_dark = (mode or "light").lower().strip() == "dark"

    brand = {
        # MIRU 핵심
        "primary":   "#05195E",   # navy (메인)
        "primary2":  "#0A2A6E",   # navy80
        "accent":    "#123A9E",   # navy60 (밝은 네이비)
        "accent2":   "#AEB7D6",   # on-navy muted (연한 블루그레이)
        "red":       "#EB0414",   # 강조 레드 (포인트 1개)
        "green":     "#24A148",

        # 모노톤
        "charcoal":  "#161616",
        "slate":     "#525252",   # ink-muted
        "steel":     "#8C8C8C",   # ink-subtle
        "fog":       "#E9ECF4",   # surface2
        "white":     "#FFFFFF",
        "pos":       "#24A148", "neg":"#EB0414",
    }
    if is_dark:
        brand.update({"ink":"#FFFFFF","muted":"#AEB7D6","line":"#6E78A8",
                      "grid":"#FFFFFF22","panel":"#FFFFFF08","bg":"none"})
    else:
        brand.update({"ink":"#161616","muted":"#525252","line":"#C7CEDC",
                      "grid":"#05195E18","panel":"#F2F4FA","bg":"none"})

    brand["tint"]=brand["line"]; brand["tint2"]=brand["fog"]; brand["spine"]=brand["line"]

    # line/patch 순환 — 네이비 계열 + 레드는 강조용으로만 따로
    mpl.rcParams["axes.prop_cycle"] = cycler(color=[
        brand["primary"], brand["accent"], brand["primary2"], brand["slate"], brand["accent2"],
    ])
    mpl.rcParams.update({
        "figure.facecolor":"none","axes.facecolor":"none","savefig.facecolor":"none",
        "text.color":brand["ink"],"axes.labelcolor":brand["ink"],"axes.titlecolor":brand["ink"],
        "xtick.color":brand["ink"],"ytick.color":brand["ink"],
        "axes.edgecolor":brand["spine"],"axes.linewidth":1.0,
        "axes.titleweight":"bold","axes.titlesize":16,"axes.labelsize":12,"font.size":12,
        "axes.grid":True,"axes.grid.axis":"y","grid.alpha":1.0,"grid.color":brand["grid"],
        "grid.linestyle":(0,(3,5)),"grid.linewidth":0.9,
        "legend.frameon":False,"legend.fontsize":10.5,
        "xtick.major.size":0,"ytick.major.size":0,
        "pdf.fonttype":42,"ps.fonttype":42,"svg.fonttype":"none",
    })
    return brand

brand = set_miru_theme(mode="light")


# =========================================================
# 3) 스타일 헬퍼 (기존 유지)
# =========================================================
def polish_axes(ax, ygrid=True, xgrid=False):
    if getattr(ax, "name", "") == "polar":
        try:
            ax.grid(alpha=1.0, linestyle=(0,(3,5)), color=brand["grid"])
            ax.tick_params(colors=brand["ink"])
        except Exception: pass
        return ax
    try:
        for side in ("top","right"):
            if side in ax.spines: ax.spines[side].set_visible(False)
        for side in ("left","bottom"):
            if side in ax.spines:
                ax.spines[side].set_color(brand["spine"]); ax.spines[side].set_linewidth(0.9)
    except Exception: pass
    try:
        ax.tick_params(axis="both", colors=brand["ink"], labelsize=10.5)
        ax.margins(x=0.03); ax.set_axisbelow(True)
        ax.yaxis.grid(ygrid)
        ax.xaxis.grid(xgrid)
        if xgrid:
            ax.xaxis.set_major_locator(plt.AutoLocator())
            ax.grid(axis="x", color=brand["grid"], linestyle=(0,(3,5)))
    except Exception: pass
    return ax


def apply_title(ax, title, subtitle=None, loc="left"):
    x = 0.0 if loc=="left" else 0.5 if loc=="center" else 1.0
    ha = "left" if loc=="left" else "center" if loc=="center" else "right"
    ax.text(x,1.12,title,transform=ax.transAxes,ha=ha,va="bottom",
            fontsize=17,fontweight="bold",color=brand["ink"],clip_on=False)
    if subtitle:
        ax.text(x,1.06,subtitle,transform=ax.transAxes,ha=ha,va="bottom",
                fontsize=10.5,color=brand["muted"],clip_on=False)
    return ax


def bar_colors(n, emphasis_idx=None):
    """차분한 네이비 계열 + 강조 막대 1개는 레드."""
    soft = [brand["accent2"], brand["line"], brand["steel"], brand["accent"], brand["primary2"]]
    colors = list(islice(cycle(soft), n))
    if emphasis_idx is not None and 0 <= emphasis_idx < n:
        colors[emphasis_idx] = brand["red"]
    return colors


def annotate_bar(ax, fmt="{:,.0f}", dy=0.02, fontsize=10, color=None, horizontal=False):
    c = color or mpl.rcParams["text.color"]
    if horizontal:
        xmax = ax.get_xlim()[1]
        for p in ax.patches:
            w = p.get_width()
            ax.text(w + xmax*dy, p.get_y()+p.get_height()/2, fmt.format(w),
                    ha="left", va="center", fontsize=fontsize, color=c, fontweight="medium")
    else:
        ymax = ax.get_ylim()[1] if len(ax.patches) else None
        for p in ax.patches:
            h = p.get_height()
            y = h + (ymax*dy if ymax else h*dy)
            ax.text(p.get_x()+p.get_width()/2, y, fmt.format(h),
                    ha="center", va="bottom", fontsize=fontsize, color=c, fontweight="medium")


def save_plot(fig, filename, w=11, h=6.2, dpi=300, transparent=True):
    global outdir
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / filename
    fig.set_size_inches(w, h)
    if transparent:
        fig.patch.set_alpha(0)
        for ax in fig.axes:
            ax.set_facecolor((1,1,1,0)); ax.patch.set_alpha(0)
    fig.savefig(str(path), dpi=dpi, bbox_inches="tight", transparent=transparent)
    plt.close(fig)
    print(f"저장: {path.name}")