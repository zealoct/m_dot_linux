
;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.
(package-initialize)

(load "~/.emacs.d/init-packages")

(add-to-list 'load-path "~/.emacs.d/custom")

(require 'setup-general)
(require 'setup-cedet)
(require 'setup-editing)
(require 'setup-c)
(require 'protobuf-mode)
;;(require 'setup-ivy-counsel)
(require 'setup-helm)
(require 'setup-helm-gtags)

(require 'sr-speedbar)
(setq speedbar-use-images nil)
(sr-speedbar-refresh-turn-off)

(require 'tablegen-mode)

;; backspace key
;; (global-set-key (kbd "C-?") 'help-command)
;; (global-set-key (kbd "C-h") 'delete-backward-char)
;; (global-set-key (kbd "M-h") 'backward-kill-word)
;; (global-set-key (kbd "M-s M-f") 'speedbar-get-focus)

;; load customized theme
(load-theme 'zea t)

(use-package yafolding
  :config
  (add-hook 'c-mode-hook 'yafolding-mode)
  (add-hook 'c++-mode-hook 'yafolding-mode)
  (define-key yafolding-mode-map (kbd "<C-S-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-M-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-return>") nil))

;; element-args
;; (require 'function-args)
;; (fa-config-default)
;; (define-key c-mode-map  [(tab)] 'company-complete)
;; (define-key c++-mode-map  [(tab)] 'company-complete)
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(ansi-color-faces-vector
   [default default default italic underline success warning error])
 '(custom-enabled-themes (quote (zea)))
 '(custom-safe-themes
   (quote
    ("1e541b85f32e32f1f5d5c3afaf1ba3d5f3262d140a09d8c1a9099493eef56a8d" "b2d5c111824b38ee4c6d13955f0772c699fc8beb63498d4a70d87093a9ffc3ea" "f0b5f1655750b2dad59c3527844d6f2acc059e5728a2569897618f53988c6c64" "21ef996bc2c565d149e8875f89fc786f9186578199d716edcb0e838beb6e5cfa" "a4c8b5a87a44f88c64dc78dd2d1b4639f6278a20ba07966420c6d8b5e4322479" "ca6676a4854f78e422f534bef36ed0100b108c0819a3f061ff9b55e0cd2bac23" "ba97e528aa6525b5fb4d9aca64c72eaad024fcc587619e0778bcce3530420de6" default)))
 '(package-selected-packages
   (quote
    (helm-ag zygospore helm-gtags helm yasnippet ws-butler volatile-highlights use-package iedit dtrt-indent counsel-projectile company clean-aindent-mode anzu)))
 '(semantic-mode t))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
(put 'downcase-region 'disabled nil)
