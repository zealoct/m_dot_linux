;;;; this library sets up package repositories and allows for syncing    packages
;;;; between different machines
;;;; to add packages to the syncing, add their repository names to the   list `pfl-packages'

;;; set up package repositories from which additional packages can be installed

;; set up ELPA and MELPA repositories
(require 'package)
(add-to-list 'package-archives
             '("melpa" . "http://melpa.org/packages/") t)
;; (add-to-list 'package-archives
;;              '("org" . "http://orgmode.org/elpa/"))
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "http://elpa.gnu.org/packages/")))

(package-initialize)

;; list of packages to sync
(setq pfl-packages
      '(
        anzu
        auto-complete
        clean-aindent-mode
        company
        company-c-headers
        counsel-projectile
        dtrt-indent
        ;;ecb
        helm
        helm-ls-git
        helm-gtags
        helm-projectile
        iedit
        markdown-mode
        markdown-mode+
        ;;rainbow-delimiters
        ;;smart-tabs-mode
        undo-tree
        use-package
        volatile-highlights
        ws-butler
        ;;xcscope
        yafolding
        yasnippet
        zygospore
        ))

;; zygospore helm-gtags helm yasnippet ws-butler volatile-highlights
;; use-package undo-tree iedit dtrt-indent counsel-projectile
;; company clean-aindent-mode anzu


;; (unless (package-installed-p 'use-package)
;;   (package-install 'use-package))

;; refresh package list if it is not already available
(when (not package-archive-contents) (package-refresh-contents))

;; install packages from the list that are not yet installed
(dolist (pkg pfl-packages)
  (when (and (not (package-installed-p pkg)) (assoc pkg package-archive-contents))
        (package-install pkg)))
