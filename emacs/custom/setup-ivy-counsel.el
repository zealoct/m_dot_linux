(use-package ivy
  :init
  (progn
    (ivy-mode 1)
    (setq ivy-use-virtual-buffers t)
    (global-set-key (kbd "C-c s") 'swiper))
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
  :bind
  (;;("M-x" . counsel-M-x)
   ;;("M-y" . counsel-yank-pop)
   ;;("C-c r" . counsel-recentf)
   ("C-c C-i C-i" . counsel-semantic-or-imenu)
   ("C-c C-i C-b" . counsel-projectile)
   ("C-c C-i C-f" . counsel-find-file)))

(use-package counsel-gtags)

(use-package counsel-projectile
  :init
  (counsel-projectile-mode))

(setq ivy-re-builders-alist
      '((t . ivy--regex-fuzzy)))

(provide 'setup-ivy-counsel)
