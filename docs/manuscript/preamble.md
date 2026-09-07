# LaTeX Preamble

LaTeX packages and commands injected into the manuscript by
`infrastructure/rendering/latex_utils.py`. Sets compact margins and
unified information-geometric notation for the rendered PDF.

```latex
% Compact document layout — denser typeset PDF while preserving footer room.
\usepackage[a4paper,top=0.65in,bottom=0.72in,left=0.65in,right=0.65in,headsep=8pt,footskip=20pt]{geometry}

% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}
\usepackage{bm}

% Theorem environments
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{lemma}[theorem]{Lemma}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{example}[theorem]{Example}
\newtheorem{remark}[theorem]{Remark}

% Document layout
\usepackage{graphicx}
\usepackage{float}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{etoolbox}
\usepackage{fvextra}
\usepackage{ragged2e}
\usepackage{hyphenat}
\usepackage{seqsplit}
\usepackage{silence}

% Monospace font with broad Unicode coverage (Greek, set theory, box-drawing,
% mathematical operators) so embedded Lean code listings render their
% literal glyphs (λ, α, ∀, ∃, ⟨, ⟩, ─, │, …) instead of falling back to
% blank boxes under lmmono. DejaVu Sans Mono ships with TeX Live's
% `dejavu-fonts-ttf` package; xelatex's kpathsea-aware fontspec picks
% it up from the texmf tree by TTF file name (no Path= needed when the
% `texlive-fontsrecommended` collection is installed, which includes
% DejaVu). fontspec is already loaded by Pandoc's xetex template via
% unicode-math; the second \usepackage{fontspec} is a no-op when
% loaded twice.
\usepackage{fontspec}
\setmonofont{DejaVuSansMono}[
  Extension=.ttf,
  BoldFont=DejaVuSansMono-Bold,
  ItalicFont=DejaVuSansMono-Oblique,
  BoldItalicFont=DejaVuSansMono-BoldOblique,
  Scale=MatchLowercase,
]

% Spacing tweaks (denser, but still readable).
\setlength{\parskip}{0.35em}
\setlength{\parindent}{0pt}
\linespread{1.05}
\raggedbottom

% PDF typography and overflow control. The manuscript contains long Lean
% declarations, Python identifiers, and method-audit tables; these settings
% give TeX more legal breakpoints instead of letting code/table cells spill
% past the margin.
\setlength{\emergencystretch}{5em}
\tolerance=2200
\pretolerance=800
\hbadness=10000
\setlength{\hfuzz}{1pt}
\WarningFilter{latex}{Label(s) may have changed}
\protected\def\breakseq#1{\seqsplit{#1}}
\protected\def\breaktt#1{\begingroup\ttfamily\seqsplit{#1}\endgroup}
\RecustomVerbatimEnvironment{Highlighting}{Verbatim}{
  commandchars=\\\{\},
  fontsize=\footnotesize,
  breaklines=true,
  breakanywhere=true,
  breaksymbolleft={},
  breakindent=1.2em
}
\AtBeginEnvironment{verbatim}{\footnotesize}
\AtBeginEnvironment{longtable}{%
  \footnotesize
  \setlength{\tabcolsep}{3pt}%
  \RaggedRight
  \emergencystretch=4em
}

% Cross-references
\usepackage{cleveref}
\usepackage{doi}
\usepackage{newunicodechar}
\newunicodechar{λ}{\ensuremath{\lambda}}
\newunicodechar{ε}{\ensuremath{\varepsilon}}
\newunicodechar{ℝ}{\ensuremath{\mathbb{R}}}
\newunicodechar{∎}{\ensuremath{\blacksquare}}
\newunicodechar{≥}{\ensuremath{\ge}}
\newunicodechar{≤}{\ensuremath{\le}}
\newunicodechar{↔}{\ensuremath{\leftrightarrow}}
\newunicodechar{⇔}{\ensuremath{\Leftrightarrow}}
\newunicodechar{⟹}{\ensuremath{\Longrightarrow}}
\newunicodechar{✓}{\ensuremath{\checkmark}}

% Common information-geometric notation
\newcommand{\KL}[2]{D_{\mathrm{KL}}\!\left(#1\,\middle\|\,#2\right)}
\newcommand{\E}[2]{\mathbb{E}_{#1}\!\left[#2\right]}
\newcommand{\Var}[2]{\mathrm{Var}_{#1}\!\left[#2\right]}
\newcommand{\policy}{\pi}
\newcommand{\policySpace}{\Pi}
\newcommand{\Mfd}{\mathcal{M}}
\newcommand{\MFsubmfd}{\mathcal{M}_{\mathrm{MF}}}
\newcommand{\MI}{I}
\newcommand{\Hent}{H}
\newcommand{\efe}{G}
\newcommand{\fe}{F}
\newcommand{\coupJ}{J}
\newcommand{\coupK}{K_c}
```
