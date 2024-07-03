;;;; this library sets up package repositories and allows for syncing    packages
;;;; between different machines
;;;; to add packages to the syncing, add their repository names to the   list `pfl-packages'

;;; set up package repositories from which additional packages can be installed

;; set up ELPA and MELPA repositories
(require 'package)
(setq package-archives
      '(("gnu-tsinghua" . "http://mirrors.tuna.tsinghua.edu.cn/elpa/gnu/")
		("melpa-tsinghua" . "http://mirrors.tuna.tsinghua.edu.cn/elpa/melpa/")))

(package-initialize)

;; list of packages to sync
;;(setq pfl-packages
;;      '( use-package ))


;; refresh package list if it is not already available
(when (not package-archive-contents) (package-refresh-contents))

;; install packages from the list that are not yet installed
;;(dolist (pkg pfl-packages)
;;  (when (and (not (package-installed-p pkg)) (assoc pkg package-archive-contents))
;;        (package-install pkg)))

(unless (package-installed-p 'use-package)
  (package-install 'use-package))
