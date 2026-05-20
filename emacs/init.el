;; Added by Package.el.  This must come before configurations of
;; installed packages.  Don't delete this line.  If you don't want it,
;; just comment it out by adding a semicolon to the start of the line.
;; You may delete these explanatory comments.

;;(load "~/.emacs.d/init-packages")
(require 'package)
(setq package-archives
      '(("gnu-tsinghua" . "http://mirrors.tuna.tsinghua.edu.cn/elpa/gnu/")
		("melpa-tsinghua" . "http://mirrors.tuna.tsinghua.edu.cn/elpa/melpa/")))

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
