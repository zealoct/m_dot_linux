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
(setq package-quickstart t) ; 把所有 -autoloads.el 合并到 package-quickstart.el 里加速启动
(package-initialize)

;; refresh package list if it is not already available
(when (not package-archive-contents) (package-refresh-contents))
;; only use-package is installed here
;; other packages are installed by use-package
(unless (package-installed-p 'use-package)
  (package-install 'use-package))

;; startup profiling: 重启后 M-x use-package-report 查看; 用完把这行删掉
(setq use-package-compute-statistics t)

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
