# LaTeX Preamble

LaTeX packages and commands injected into the manuscript by
`infrastructure/rendering/latex_utils.py`. Sets tighter margins and
unified information-geometric notation for the rendered PDF.

```latex
% Tighter document layout — denser typeset PDF.
\usepackage[a4paper,top=0.85in,bottom=0.95in,left=0.85in,right=0.85in,headsep=10pt,footskip=24pt]{geometry}

% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}
\usepackage{mathtools}
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

% Spacing tweaks (denser, but still readable).
\setlength{\parskip}{0.35em}
\setlength{\parindent}{0pt}
\linespread{1.05}

% Cross-references
\usepackage{cleveref}
\usepackage{doi}
\usepackage{newunicodechar}

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
