;; Per-language modes and per-mode configuration

;; ---- C / C++ ----

(use-package cc-mode
  :ensure nil ; built-in
  :defer t
  :init
  ;; folding
  (add-hook 'c-mode-common-hook 'hs-minor-mode)
  ;; indentation & whitespace
  (add-hook 'c-mode-common-hook
            (lambda ()
              (setq tab-width 4
                    c-basic-offset tab-width
                    indent-tabs-mode nil)
              (c-set-offset 'arglist-intro '++)
              (c-set-offset 'arglist-cont '0)
              (c-set-offset 'arglist-cont-nonempty '(c-lineup-argcont
                                                     c-lineup-gcc-asm-reg
                                                     c-lineup-arglist))
              (c-set-offset 'arglist-close 0)
              (c-set-offset 'innamespace 0)
              (c-set-offset 'namespace-open 0)
              (c-set-offset 'namespace-close 0)
              (c-set-offset 'statement-cont '(c-lineup-string-cont
                                              c-lineup-cascaded-calls
                                              c-lineup-math))
              (c-set-offset 'substatement-open 0)
              (c-set-offset 'brace-list-intro '+)
              (setq whitespace-line-column 120)
              (whitespace-mode t))))

;; block folding, C/C++ only
(use-package yafolding
  :ensure t
  :hook ((c-mode c++-mode) . yafolding-mode)
  :config
  (define-key yafolding-mode-map (kbd "<C-S-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-M-return>") nil)
  (define-key yafolding-mode-map (kbd "<C-return>")   nil))

(use-package cuda-mode
  :ensure t
  :mode (("\\.cu\\'"  . cuda-mode)
         ("\\.cuh\\'" . cuda-mode)))

;; ---- Rust ----

(use-package rust-mode
  :ensure t
  :mode ("\\.rs\\'" . rust-mode))

;; ---- Build systems ----

(use-package cmake-mode
  :ensure t
  :mode (("\\`CMakeLists\\.txt\\'" . cmake-mode)
         ("\\.cmake\\'"            . cmake-mode)))

;; ---- Data / config formats ----

(use-package json-mode
  :ensure t
  :mode ("\\.json\\'" . json-mode))

;; ---- Markdown ----

(use-package markdown-mode
  :ensure t
  :mode (("README\\.md\\'" . gfm-mode)
         ("\\.md\\'"       . markdown-mode)
         ("\\.markdown\\'" . markdown-mode))
  :init
  (setq markdown-fontify-code-blocks-natively t))

;; ---- Vendored modes (not on MELPA/ELPA) ----

(use-package protobuf-mode
  :ensure nil ; vendored in custom/
  :mode ("\\.proto\\'" . protobuf-mode))

(use-package tablegen-mode
  :ensure nil ; vendored in custom/
  :mode ("\\.td\\'" . tablegen-mode))

(provide 'setup-languages)
