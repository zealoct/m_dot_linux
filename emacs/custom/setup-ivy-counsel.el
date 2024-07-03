;;(use-package ivy
;;  :init
;;  (progn
;;    (ivy-mode 1)
;;    (setq ivy-use-virtual-buffers t)
;;    (global-set-key (kbd "C-c s") 'swiper))
;;  )

(use-package ivy
  :ensure t
  :diminish (ivy-mode . "")
  :bind
  (:map ivy-mode-map
        ("C-c s" . swiper-thing-at-point))
  :config
  (ivy-mode 1)
  ;; add ‘recentf-mode’ and bookmarks to ‘ivy-switch-buffer’.
  (setq ivy-use-virtual-buffers t)
  ;; number of result lines to display
  (setq ivy-height 20)
  ;; does not count candidates
  (setq ivy-count-format "")
  ;; no regexp by default
  ;;(setq ivy-initial-inputs-alist nil)
  ;; configure regexp engine.
  ;;(setq ivy-re-builders-alist
  ;;      ;; allow input not in order
  ;;      '((t   . ivy--regex-ignore-order)))
  )

;;(require 'ivy-posframe)
;; display at `ivy-posframe-style'
;;(setq ivy-posframe-display-functions-alist '((t . ivy-posframe-display)))
;; (setq ivy-posframe-display-functions-alist '((t . ivy-posframe-display-at-frame-center)))
;; (setq ivy-posframe-display-functions-alist '((t . ivy-posframe-display-at-window-center)))
;;(setq ivy-posframe-display-functions-alist '((t . ivy-posframe-display-at-frame-bottom-left)))
;; (setq ivy-posframe-display-functions-alist '((t . ivy-posframe-display-at-window-bottom-left)))
;;(ivy-posframe-mode 1)

(use-package counsel
  :ensure t
  :bind
  (("M-x" . counsel-M-x)
   ;;("M-y" . counsel-yank-pop)
   ("C-c r" . counsel-recentf)
   ("C-c C-i C-i" . counsel-semantic-or-imenu)
   ("C-x b" . counsel-switch-buffer)
   ("C-x C-f" . counsel-find-file)
   ))

(use-package counsel-gtags
  :ensure t
  :bind-keymap ("C-c g" . counsel-gtags-command-map)
  :bind (("C-]" . counsel-gtags-find-dwin)
         ("C-t" . counsel-gtags-go-backward)
         ;;("C-c g d" . counsel-gtags-find-definition)
         ;;("C-c g r" . counsel-gtags-find-reference)
         ;;("C-c g u" . counsel-gtags-update-tags)
         )
  :config
  (counsel-gtags-mode 1)
  (setq counsel-gtags-debug-mode 1)
  )

;;  :bind
;;  (("C-c g d" . counsel-gtags-find-definition)
;;   ("C-c g f" . counsel-gtags-find-file)
;;   ("C-c g i" . counsel-gtags-find-dwim)
;;   ("C-c g s" . counsel-gtags-find-symbol)
;;   ("C-c g r" . counsel-gtags-find-reference)
;;   ("C-c g u" . counsel-gtags-update-tags)
;;   ))

(use-package counsel-projectile :ensure t
  :init (use-package ag :ensure t)

  :config
  (counsel-projectile-mode)
  (setq counsel-projectile-ag-initial-input `(ivy-thing-at-point))

  :bind
  (("C-x C-b" . counsel-projectile)
   ("C-c h p" . counsel-projectile-ag)
   )
  )

;;(setq ivy-re-builders-alist
;;      '((t . ivy--regex-fuzzy)))

(provide 'setup-ivy-counsel)
