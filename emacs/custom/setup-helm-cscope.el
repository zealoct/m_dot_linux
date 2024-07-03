(use-package helm-cscope
  :init
  (progn
    ;; Enable helm-cscope-mode
    (add-hook 'c-mode-hook 'helm-cscope-mode)
    (add-hook 'c++-mode-hook 'helm-cscope-mode)
    ;; Set key bindings
    (with-eval-after-load 'helm-cscope
      (define-key helm-cscope-mode-map (kbd "C-c g s") 'helm-cscope-find-this-symbol)
      (define-key helm-cscope-mode-map (kbd "C-c g g") 'helm-cscope-find-global-definition)
      (define-key helm-cscope-mode-map (kbd "C-c g r") 'helm-cscope-find-called-function)
      (define-key helm-cscope-mode-map (kbd "C-c g t") 'helm-cscope-find-calling-this-funtcion)
      (define-key helm-cscope-mode-map (kbd "C-c g a") 'helm-cscope-select))))

(provide 'setup-helm-cscope)
