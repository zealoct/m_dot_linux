;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.

;;(load "~/.emacs.d/init-packages")
(require 'package)
(setq package-archives
      '(("gnu-tsinghua" . "https://mirrors.tuna.tsinghua.edu.cn/elpa/gnu/")
		("melpa-tsinghua" . "https://mirrors.tuna.tsinghua.edu.cn/elpa/melpa/")))

(setq package-check-signature nil)
(package-initialize)

;; refresh package list if it is not already available
(when (not package-archive-contents) (package-refresh-contents))
;; only use-package is installed here
;; other packages are installed by use-package
(unless (package-installed-p 'use-package)
  (package-install 'use-package))

;; Load customed init script
(add-to-list 'load-path "~/.emacs.d/custom")
(require 'custom-init)
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages nil))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
