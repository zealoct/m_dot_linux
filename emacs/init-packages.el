;;;; this library sets up package repositories and allows for syncing    packages
;;;; between different machines
;;;; to add packages to the syncing, add their repository names to the   list `pfl-packages'

;;; set up package repositories from which additional packages can be installed

;; set up ELPA and MELPA repositories
(require 'package)
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/") t)
;; (add-to-list 'package-archives
;;              '("org" . "http://orgmode.org/elpa/"))
(when (< emacs-major-version 24)
  ;; For important compatibility libraries like cl-lib
  (add-to-list 'package-archives '("gnu" . "http://elpa.gnu.org/packages/")))

;; list of packages to sync
(setq pfl-packages
      '(
        auto-complete
        markdown-mode
        markdown-mode+
        rainbow-delimiters
        smart-tabs-mode
        xcscope
        ))

(package-initialize)

;; refresh package list if it is not already available
(when (not package-archive-contents) (package-refresh-contents))

;; install packages from the list that are not yet installed
(dolist (pkg pfl-packages)
  (when (and (not (package-installed-p pkg)) (assoc pkg package-archive-contents))
        (package-install pkg)))
