;; this variables must be set before load helm-gtags
;; you can change to any prefix key of your choice
(use-package helm-gtags
  :ensure t
  :bind (:map helm-gtags-mode-map
              ("C-c g a" . helm-gtags-tags-in-this-function)
              ("C-c g d" . helm-gtags-dwim)
              ("C-c g r" . helm-gtags-find-rtag)
              ("C-c g f" . helm-gtags-parse-file)
              ("C-c g o" . helm-gtags-pop-stack)
              )
  :config
  (setq helm-gtags-ignore-case t)
  (setq helm-gtags-auto-update t)
  (setq helm-gtags-use-input-at-cursor t)
  (setq helm-gtags-pulse-at-cursor t)
  (setq helm-gtags-prefix-key "\C-cg")
  ;;(setq helm-gtags-suggested-key-mapping t)

  :init
  (progn
    ;; Enable helm-gtags-mode in Dired so you can jump to any tag
    ;; when navigate project tree with Dired
    (add-hook 'dired-mode-hook 'helm-gtags-mode)

    ;; Enable helm-gtags-mode in Eshell for the same reason as above
    (add-hook 'eshell-mode-hook 'helm-gtags-mode)

    ;; Enable helm-gtags-mode in languages that GNU Global supports
    (add-hook 'c-mode-hook 'helm-gtags-mode)
    (add-hook 'c++-mode-hook 'helm-gtags-mode)
    (add-hook 'java-mode-hook 'helm-gtags-mode)
    (add-hook 'asm-mode-hook 'helm-gtags-mode)
    ))

(provide 'setup-helm-gtags)
