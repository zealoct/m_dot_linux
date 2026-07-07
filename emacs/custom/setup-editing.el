;; Editing behavior: indentation, kill/yank, whitespace, minor modes

;; ---- indentation (single source of truth) ----
(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)
(add-hook 'sh-mode-hook (lambda () (setq tab-width 4)))

;; ---- kill/mark ring, newline policy ----
(setq global-mark-ring-max 5000
      mark-ring-max        5000
      kill-ring-max        5000
      mode-require-final-newline t
      kill-whole-line      t)

;; ---- coding system ----
(set-terminal-coding-system 'utf-8)
(set-keyboard-coding-system 'utf-8)
(set-language-environment  "UTF-8")
(prefer-coding-system 'utf-8)

;; ---- basic editing behavior ----
(delete-selection-mode)
(global-set-key (kbd "RET")   'newline-and-indent)
(global-set-key (kbd "C-M-n") 'scroll-up-line)
(global-set-key (kbd "C-M-p") 'scroll-down-line)
(global-set-key (kbd "M-;")   'comment-dwim-2)

;; imenu function name in mode-line
(add-hook 'prog-mode-hook #'which-function-mode)

;; show trailing whitespace when programming
(add-hook 'prog-mode-hook
          (lambda () (setq show-trailing-whitespace 1)))

;; ---- whitespace visualization ----
(global-set-key (kbd "C-c w") 'whitespace-mode)
(use-package whitespace
  :ensure nil ; built-in
  :defer t
  :config
  (setq whitespace-style       '(face empty tabs lines-tail trailing)
        whitespace-line-column 100))

;; detailed whitespace in diff-mode
(add-hook 'diff-mode-hook
          (lambda ()
            (setq-local whitespace-style
                        '(face tabs tab-mark spaces space-mark
                               trailing indentation::space indentation::tab
                               newline newline-mark))
            (whitespace-mode 1)))

;; ---- packages ----

(use-package volatile-highlights
  :ensure t
  :hook (after-init . volatile-highlights-mode))

(use-package yasnippet
  :ensure t
  :defer t
  :init (add-hook 'prog-mode-hook 'yas-minor-mode))

(use-package clean-aindent-mode
  :ensure t
  :hook (prog-mode . clean-aindent-mode))

(use-package dtrt-indent
  :ensure t
  :init (setq dtrt-indent-verbosity 0)
  :hook (after-init . dtrt-indent-mode))

(use-package ws-butler
  :ensure t
  :hook ((prog-mode text-mode fundamental-mode) . ws-butler-mode))

(use-package iedit
  :ensure t
  :bind (("C-;" . iedit-mode))
  :init (setq iedit-toggle-key-default nil))

;; ---- Prelude-derived helpers ----

;; Smart C-a: toggle between first non-whitespace and BOL
(defun prelude-move-beginning-of-line (arg)
  "Move point back to indentation of beginning of line.

Move point to the first non-whitespace character on this line.
If point is already there, move to the beginning of the line.
Effectively toggle between the first non-whitespace character and
the beginning of the line."
  (interactive "^p")
  (setq arg (or arg 1))
  (when (/= arg 1)
    (let ((line-move-visual nil))
      (forward-line (1- arg))))
  (let ((orig-point (point)))
    (back-to-indentation)
    (when (= orig-point (point))
      (move-beginning-of-line 1))))
(global-set-key (kbd "C-a") 'prelude-move-beginning-of-line)

;; Copy/cut whole line when no region is active
(defadvice kill-ring-save (before slick-copy activate compile)
  "When called interactively with no active region, copy a single
line instead."
  (interactive
   (if mark-active (list (region-beginning) (region-end))
     (message "Copied line")
     (list (line-beginning-position)
           (line-beginning-position 2)))))

(defadvice kill-region (before slick-cut activate compile)
  "When called interactively with no active region, kill a single
line instead."
  (interactive
   (if mark-active (list (region-beginning) (region-end))
     (list (line-beginning-position)
           (line-beginning-position 2)))))

;; kill-line also munches whitespace on next line (C-family + Lisp)
(defadvice kill-line (before check-position activate)
  (if (member major-mode
              '(emacs-lisp-mode scheme-mode lisp-mode
                                c-mode c++-mode objc-mode
                                latex-mode plain-tex-mode))
      (if (and (eolp) (not (bolp)))
          (progn (forward-char 1)
                 (just-one-space 0)
                 (backward-char 1)))))

;; Auto-indent yanked text in prog-mode
(defvar yank-indent-modes
  '(LaTeX-mode TeX-mode)
  "Modes in which to indent regions that are yanked (or yank-popped).
Only modes that don't derive from `prog-mode' should be listed here.")

(defvar yank-indent-blacklisted-modes
  '(python-mode slim-mode haml-mode)
  "Modes for which auto-indenting is suppressed.")

(defvar yank-advised-indent-threshold 1000
  "Threshold (# chars) over which indentation does not automatically occur.")

(defun yank-advised-indent-function (beg end)
  "Do indentation, as long as the region isn't too large."
  (if (<= (- end beg) yank-advised-indent-threshold)
      (indent-region beg end nil)))

(defadvice yank (after yank-indent activate)
  "If current mode is one of 'yank-indent-modes,
indent yanked text (with prefix arg don't indent)."
  (if (and (not (ad-get-arg 0))
           (not (member major-mode yank-indent-blacklisted-modes))
           (or (derived-mode-p 'prog-mode)
               (member major-mode yank-indent-modes)))
      (let ((transient-mark-mode nil))
        (yank-advised-indent-function (region-beginning) (region-end)))))

(defadvice yank-pop (after yank-pop-indent activate)
  "If current mode is one of `yank-indent-modes',
indent yanked text (with prefix arg don't indent)."
  (when (and (not (ad-get-arg 0))
             (not (member major-mode yank-indent-blacklisted-modes))
             (or (derived-mode-p 'prog-mode)
                 (member major-mode yank-indent-modes)))
    (let ((transient-mark-mode nil))
      (yank-advised-indent-function (region-beginning) (region-end)))))

;; Indent buffer or region
(defun indent-buffer ()
  "Indent the currently visited buffer."
  (interactive)
  (indent-region (point-min) (point-max)))

(defcustom prelude-indent-sensitive-modes
  '(coffee-mode python-mode slim-mode haml-mode yaml-mode)
  "Modes for which auto-indenting is suppressed."
  :type 'list)

(defun indent-region-or-buffer ()
  "Indent a region if selected, otherwise the whole buffer."
  (interactive)
  (unless (member major-mode prelude-indent-sensitive-modes)
    (save-excursion
      (if (region-active-p)
          (progn
            (indent-region (region-beginning) (region-end))
            (message "Indented selected region."))
        (progn
          (indent-buffer)
          (message "Indented buffer.")))
      (whitespace-cleanup))))
(global-set-key (kbd "C-c i") 'indent-region-or-buffer)

;; Smart open-line (M-o)
(defun prelude-smart-open-line (arg)
  "Insert an empty line after the current line.
Position the cursor at its beginning, according to the current mode.
With a prefix ARG open line above the current line."
  (interactive "P")
  (if arg
      (prelude-smart-open-line-above)
    (progn
      (move-end-of-line nil)
      (newline-and-indent))))

(defun prelude-smart-open-line-above ()
  "Insert an empty line above the current line.
Position the cursor at it's beginning, according to the current mode."
  (interactive)
  (move-beginning-of-line nil)
  (newline-and-indent)
  (forward-line -1)
  (indent-according-to-mode))

(global-set-key (kbd "M-o") 'prelude-smart-open-line)

(provide 'setup-editing)
