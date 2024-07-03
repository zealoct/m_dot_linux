(menu-bar-mode -1)
(if (functionp 'tool-bar-mode)
    (tool-bar-mode -1))

(setq gc-cons-threshold 100000000)
(setq inhibit-startup-message t)

(defalias 'yes-or-no-p 'y-or-n-p)

;; show unncessary whitespace that can mess up your diff
(add-hook 'prog-mode-hook
          (lambda () (interactive)
            (setq show-trailing-whitespace 1)))

;; use space to indent by default
(setq-default indent-tabs-mode nil)

;; set appearance of a tab that is represented by 4 spaces
(setq-default tab-width 4)

;; Compilation
;;(global-set-key (kbd "<f5>") (lambda ()
;;                               (interactive)
;;                               (setq-local compilation-read-command nil)
;;                               (call-interactively 'compile)))

;; setup autosave directory
(setq temporary-file-directory "~/.emacs_saves")
(setq backup-directory-alist
      `((".*" . ,temporary-file-directory)))
(setq auto-save-file-name-transforms
      `((".*" ,temporary-file-directory t)))

;; show column number by default
(setq column-number-mode t)

;; shortcuts for fast window shrinking
(global-set-key (kbd "<C-up>") 'shrink-window)
(global-set-key (kbd "<C-down>") 'enlarge-window)
(global-set-key (kbd "<C-left>") 'shrink-window-horizontally)
(global-set-key (kbd "<C-right>") 'enlarge-window-horizontally)
(global-set-key (kbd "<M-.>") 'previous-buffer)

;; setup GDB
(setq
 ;; use gdb-many-windows by default
 gdb-many-windows t

 ;; Non-nil means display source file containing the main routine at startup
 gdb-show-main t
 )

;; company
(use-package company
  :init
  (global-company-mode 1)
  (setq company-dabbrev-downcase 0)
  (setq company-idle-delay 1.5)
  (setq company-backends
        '((company-files          ; files & directory
           company-keywords       ; keywords
           company-yasnippet)
          (company-capf company-abbrev company-dabbrev)
          )))

;; (define-key c-mode-map  [(control tab)] 'company-complete)
;; (define-key c++-mode-map  [(control tab)] 'company-complete)

;; Package: projejctile
(use-package projectile
  :init
  (projectile-global-mode)
  (setq projectile-enable-caching t))

;; Package zygospore
(use-package zygospore
  :bind (("C-x 1" . zygospore-toggle-delete-other-windows)
         ("RET" .   newline-and-indent)))

;; automatically indent when press RET

;; activate whitespace-mode to view all whitespace characters
(global-set-key (kbd "C-c w") 'whitespace-mode)
(windmove-default-keybindings)

;; whitespace
(require 'whitespace)
(setq whitespace-style '(face empty tabs lines-tail trailing))
;;(setq whitespace-line-column 100)
;;(global-whitespace-mode nil)

;; automatically show paren
(show-paren-mode 1)

;; auto detect file changes on disk
(global-auto-revert-mode 1)

(provide 'setup-general)
