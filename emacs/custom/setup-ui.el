;; UI, session, window/buffer management

(menu-bar-mode -1)
(if (functionp 'tool-bar-mode)
    (tool-bar-mode -1))

(setq gc-cons-threshold 100000000)
(setq inhibit-startup-message t)

(defalias 'yes-or-no-p 'y-or-n-p)

(setq column-number-mode t)

;; backups and auto-saves out of the way
(setq temporary-file-directory "~/.emacs_saves")
(setq backup-directory-alist
      `((".*" . ,temporary-file-directory)))
(setq auto-save-file-name-transforms
      `((".*" ,temporary-file-directory t)))

;; window resize with C-<arrow>
(global-set-key (kbd "<C-up>")    'shrink-window)
(global-set-key (kbd "<C-down>")  'enlarge-window)
(global-set-key (kbd "<C-left>")  'shrink-window-horizontally)
(global-set-key (kbd "<C-right>") 'enlarge-window-horizontally)

;; quick switch to previous buffer
(defun switch-to-previous-buffer ()
  (interactive)
  (switch-to-buffer (other-buffer (current-buffer) 1)))
(global-unset-key (kbd "<C-M-l>"))
(global-set-key   (kbd "<C-M-l>") 'switch-to-previous-buffer)

;; shift-arrows to move between windows
(windmove-default-keybindings)

;; toggle one-window / restore
(use-package zygospore
  :ensure t
  :bind (("C-x 1" . zygospore-toggle-delete-other-windows)))

(global-auto-revert-mode 1)
(show-paren-mode 1)

;; GDB
(setq gdb-many-windows t
      gdb-show-main t)

(provide 'setup-ui)
