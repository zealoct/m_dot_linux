;; .emacs
(global-set-key (kbd "C-?") 'help-command)
(global-set-key (kbd "C-h") 'delete-backward-char)
(global-set-key (kbd "M-h") 'backward-kill-word)

(package-initialize) ;; You might already have this line
(load "~/.emacs.d/init-packages")

;; default to better frame titles
(setq frame-title-format
      (concat  "%b - emacs@" (system-name)))
;; default to unified diffs
(setq diff-switches "-u")

;; always end a file with a newline
;(setq require-final-newline 'query)

;;; uncomment for CJK utf-8 support for non-Asian users
;; (require 'un-define)


;; enable AC mode by default
(global-auto-complete-mode t)

(setq column-number-mode t)

(setq-default speedbar t)

;; Intent Settings
;;
(setq-default indent-tabs-mode nil)
(setq-default tab-width 4)
(setq c-default-style "linux"
      c-basic-offset 4)

(add-hook 'c-mode-common-hook
          (lambda ()
            (c-set-offset 'arglist-intro '++)
            (c-set-offset 'arglist-cont '++)
            (c-set-offset 'arglist-close 0)
            (c-set-offset 'innamespace 0)
            (c-set-offset 'namespace-open 0)
            (c-set-offset 'namespace-close 0)))

;; Cscope
(require 'xcscope)
(cscope-setup)

;; CEDET
(global-ede-mode 1)
(require 'semantic/sb)
(semantic-mode 1)

;; ECB
(require 'ecb)

;; whitespace
(require 'whitespace)
(setq whitespace-style '(face empty tabs lines-tail trailing))
(setq whitespace-line-column 100)
(global-whitespace-mode t)
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(ansi-color-faces-vector
   [default default default italic underline success warning error])
 '(ansi-color-names-vector
   ["#2e3436" "#a40000" "#4e9a06" "#c4a000" "#204a87" "#5c3566" "#729fcf" "#eeeeec"])
 '(custom-enabled-themes (quote (zea)))
 '(custom-safe-themes
   (quote
    ("3b5ce826b9c9f455b7c4c8bff22c020779383a12f2f57bf2eb25139244bb7290" "44c566df0e1dfddc60621711155b1be4665dd3520b290cb354f8270ca57f8788" "ba97e528aa6525b5fb4d9aca64c72eaad024fcc587619e0778bcce3530420de6" default)))
 '(fci-rule-color "#6a737d")
 '(nrepl-message-colors
   (quote
    ("#032f62" "#6a737d" "#d73a49" "#6a737d" "#005cc5" "#6f42c1" "#d73a49" "#6a737d")))
 '(pdf-view-midnight-colors (quote ("#6a737d" . "#fffbdd")))
 '(vc-annotate-background "#3390ff")
 '(vc-annotate-color-map
   (quote
    ((20 . "#6a737d")
     (40 . "#032f62")
     (60 . "#6a737d")
     (80 . "#6a737d")
     (100 . "#6a737d")
     (120 . "#d73a49")
     (140 . "#6a737d")
     (160 . "#6a737d")
     (180 . "#6a737d")
     (200 . "#6a737d")
     (220 . "#22863a")
     (240 . "#005cc5")
     (260 . "#6f42c1")
     (280 . "#6a737d")
     (300 . "#005cc5")
     (320 . "#6a737d")
     (340 . "#d73a49")
     (360 . "#6a737d"))))
 '(vc-annotate-very-old-color "#6a737d"))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

;; automatically show paren
(show-paren-mode 1)
(load-theme 'zea t)
