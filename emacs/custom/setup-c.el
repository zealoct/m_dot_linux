;; company-c-headers
(use-package company-c-headers)

(setq company-backends
      '((company-gtags
         company-semantic
         company-capf)
        (company-c-headers
         company-files          ; files & directory
         company-keywords       ; keywords
         company-yasnippet)))

;;(company-mode)

(use-package cc-mode
  :init
  ;;(define-key c-mode-map  [(tab)] 'company-complete)
  ;;(define-key c++-mode-map  [(tab)] 'company-complete)

  ;; hs-minor-mode for folding source code
  (add-hook 'c-mode-common-hook 'hs-minor-mode)

  ;; Intent Settings
  ;;
  (add-hook 'c-mode-common-hook
            (lambda ()
              (message "c-mode-hooked")
              (setq tab-width 4)
              (setq c-basic-offset tab-width)
              (setq indent-tabs-mode nil)
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
              (whitespace-mode t)
              )
            )

  )


;; Available C style:
;; “gnu”: The default style for GNU projects
;; “k&r”: What Kernighan and Ritchie, the authors of C used in their book
;; “bsd”: What BSD developers use, aka “Allman style” after Eric Allman.
;; “whitesmith”: Popularized by the examples that came with Whitesmiths C, an early commercial C compiler.
;; “stroustrup”: What Stroustrup, the author of C++ used in his book
;; “ellemtel”: Popular C++ coding standards as defined by “Programming in C++, Rules and Recommendations,” Erik Nyquist and Mats Henricson, Ellemtel
;; “linux”: What the Linux developers use for kernel development
;; “python”: What Python developers use for extension modules
;; “java”: The default style for java-mode (see below)
;; “user”: When you want to define your own style
;; (setq c-default-style) "linux" ;; set style to "linux"


(provide 'setup-c)
