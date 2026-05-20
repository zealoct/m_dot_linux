(require 'setup-general)
;;(require 'setup-cedet)
(require 'setup-editing)
(require 'setup-c)
(require 'setup-rust)
(require 'protobuf-mode)

(cond
 ((eq system-type 'darwin)
  ;; Ivy counsel
  ;;(require 'setup-ivy-counsel)
  ;;
  ;; Helm
  ;;(require 'setup-helm)
  ;;(require 'setup-helm-gtags)
  ;;
  ;; Vertico + Consult + Orderless
  (require 'setup-vertico)
  (setq mac-option-key-is-meta nil)
  (setq mac-command-key-is-meta t)
  (setq mac-command-modifier 'meta)
  (setq mac-option-modifier nil)
  )
 ((eq system-type 'gnu/linux)
  ;;(require 'setup-helm)
  ;;(require 'setup-helm-gtags)))
  (require 'setup-vertico)
  )
 )

;;(require 'sr-speedbar)
;;(setq speedbar-use-images nil)
;;(sr-speedbar-refresh-turn-off)

(require 'tablegen-mode)

(use-package cmake-mode :ensure t)

(use-package yafolding :ensure t
  :config
  (add-hook 'c-mode-hook 'yafolding-mode)
  (add-hook 'c++-mode-hook 'yafolding-mode)
  (define-key yafolding-mode-map (kbd "<C-S-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-M-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-return>") nil))

(use-package json-mode :ensure t)

;; backspace key
;; (global-set-key (kbd "C-?") 'help-command)
;; (global-set-key (kbd "C-h") 'delete-backward-char)
;; (global-set-key (kbd "M-h") 'backward-kill-word)
;; (global-set-key (kbd "M-s M-f") 'speedbar-get-focus)

;; load customized theme
;;(if window-system
;;    (load-theme 'tsdh-light t)
;;  (load-theme 'tsdh-light t))

(provide 'custom-init)
