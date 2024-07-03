;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.

(load "~/.emacs.d/init-packages")

(add-to-list 'load-path "~/.emacs.d/custom")

(require 'setup-general)
(require 'setup-cedet)
(require 'setup-editing)
(require 'setup-c)
(require 'setup-rust)
(require 'protobuf-mode)

(cond
 ((eq system-type 'darwin)
  ;;(require 'setup-ivy-counsel)
  (require 'setup-helm)
  (require 'setup-helm-gtags)
  (setq mac-option-key-is-meta nil)
  (setq mac-command-key-is-meta t)
  (setq mac-command-modifier 'meta)
  (setq mac-option-modifier nil))
 ((eq system-type 'gnu/linux)
  (require 'setup-helm)
  (require 'setup-helm-gtags)))

;;(require 'sr-speedbar)
;;(setq speedbar-use-images nil)
;;(sr-speedbar-refresh-turn-off)

(require 'tablegen-mode)

(use-package yafolding :ensure t
  :config
  (add-hook 'c-mode-hook 'yafolding-mode)
  (add-hook 'c++-mode-hook 'yafolding-mode)
  (define-key yafolding-mode-map (kbd "<C-S-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-M-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-return>") nil))

;; backspace key
;; (global-set-key (kbd "C-?") 'help-command)
;; (global-set-key (kbd "C-h") 'delete-backward-char)
;; (global-set-key (kbd "M-h") 'backward-kill-word)
;; (global-set-key (kbd "M-s M-f") 'speedbar-get-focus)

;; load customized theme
(if window-system
    (load-theme 'tsdh-light t)
  (load-theme 'zea t))

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(default ((t (:inherit nil :inverse-video nil :box nil :strike-through nil :overline nil :underline nil :slant normal :weight normal :height 140 :width normal :foundry "nil" :family "PragmataPro"))))
 '(ansi-color-faces-vector [default default default italic underline success warning error])
 '(custom-enabled-themes '(zea))
 '(custom-safe-themes '("1e541b85f32e32f1f5d5c3afaf1ba3d5f3262d140a09d8c1a9099493eef56a8d" "b2d5c111824b38ee4c6d13955f0772c699fc8beb63498d4a70d87093a9ffc3ea" "f0b5f1655750b2dad59c3527844d6f2acc059e5728a2569897618f53988c6c64" "21ef996bc2c565d149e8875f89fc786f9186578199d716edcb0e838beb6e5cfa" "a4c8b5a87a44f88c64dc78dd2d1b4639f6278a20ba07966420c6d8b5e4322479" "ca6676a4854f78e422f534bef36ed0100b108c0819a3f061ff9b55e0cd2bac23" "ba97e528aa6525b5fb4d9aca64c72eaad024fcc587619e0778bcce3530420de6" default))
 '(package-selected-packages '(counsel-ag-popup gnu-elpa gnu-elpa-keyring-update helm-ag zygospore helm-gtags helm yasnippet ws-butler volatile-highlights use-package iedit dtrt-indent counsel-projectile company clean-aindent-mode anzu))
 '(semantic-mode t))

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(ansi-color-names-vector
   ["#212526" "#ff4b4b" "#b4fa70" "#fce94f" "#729fcf" "#e090d7" "#8cc4ff" "#eeeeec"])
 '(custom-enabled-themes '(zea))
 '(custom-safe-themes
   '("0c7772b3c47ed86abc7399d0c8a0305eefdeefd262b1c2845fa24aeea7169830" "4b218487556ebe77be6474924611409ce653c52928ddd9f2f26c465a5ce932af" "353c362f41128aeb3fa343dd71f7ae1d3ee8f6978070ab6d3f6ab20b958b5e54" "2791abe3592ba49e43a38869469695f41a32b0c0bc9362889668695133446757" "1e541b85f32e32f1f5d5c3afaf1ba3d5f3262d140a09d8c1a9099493eef56a8d" default))
 '(package-selected-packages
   '(zygospore yasnippet yafolding ws-butler volatile-highlights use-package swiper-helm markdown-mode+ ivy-posframe iedit helm-swoop helm-projectile helm-ls-git helm-gtags helm-ag dtrt-indent counsel-projectile counsel-gtags company-c-headers clean-aindent-mode auto-complete anzu)))
