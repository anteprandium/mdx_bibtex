mdx_bibtex
==========

A proof-of-concept bibtex extension for Python markdown.



## Loading a bibliography

First of all, you need to indicate a bibliography to use this extension. You can do that from python, 

    import markdown
    import mdx_bibtex
    md=markdown.Markdown(extensions=['bib(bibliography=example.bib)'])
    
or, if you are using the `Meta` extension, with the `Meta` key `bibliography`

    Bibliography: example.bib
    Title: Nifty title
    
    Neat, you're ready to use the bibliography.
    
    
## Using the bibliography

Supported syntax.

<table>
<thead>
<tr>
<th>Use</th>
<th>To get</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>@(wiles95)</code></td>
<td><a class="citation" data-key="wiles95" data-locator="" data-modifier="" data-prefix="" href="#wiles95">(Wiles 1995)</a></td>
</tr>
<tr>
<td><code>@(wiles95,bennet70)</code></td>
<td><span class="citation-multiple"><span class="citation-open-par">(</span><a class="citation" data-key="wiles95" data-locator="" data-modifier="" data-prefix="" href="#wiles95">Wiles 1995</a><span class="citation-comma">, </span><a class="citation" data-key="bennet70" data-locator="" data-modifier="" data-prefix="" href="#bennet70">Bennett 1970</a><span class="citation-close-par">)</span></span></td>
</tr>
<tr>
<td><code>@(wiles95)[p. 11]</code></td>
<td><a class="citation" data-key="wiles95" data-locator="p. 11" data-modifier="" data-prefix="" href="#wiles95">(Wiles 1995, p. 11)</a></td>
</tr>
<tr>
<td><code>@[see](wiles95)</code></td>
<td><a class="citation" data-key="wiles95" data-locator="" data-modifier="" data-prefix="see" href="#wiles95">(see Wiles 1995)</a></td>
</tr>
<tr>
<td><code>@[see](wiles95)[p. 11]</code></td>
<td><a class="citation" data-key="wiles95" data-locator="p. 11" data-modifier="" data-prefix="see" href="#wiles95">(see Wiles 1995, p. 11)</a></td>
</tr>
<tr>
<td><code>@+(wiles95)</code></td>
<td><a class="citation" data-key="wiles95" data-locator="" data-modifier="author-only" data-prefix="" href="#wiles95">Wiles</a></td>
</tr>
<tr>
<td><code>@-(wiles95)</code></td>
<td><a class="citation" data-key="wiles95" data-locator="" data-modifier="year-only" data-prefix="" href="#wiles95">(1995)</a></td>
</tr>
<tr>
<td><code>@.(wiles95)</code></td>
<td><a class="citation" data-key="wiles95" data-locator="" data-modifier="no-paren" data-prefix="" href="#wiles95">Wiles 1995</a></td>
</tr>
<tr>
<td><code>@/(wiles95)</code></td>
<td>Nothing, equivalent of <code>\nocite{wiles95}</code></td>
</tr>
<tr>
<td><code>@/(*)</code></td>
<td>Nothing, equivalent of <code>\nocite{*}</code></td>
</tr>
</tbody>
</table>


At the end of the document, use `[REFERENCES]` to indicate where your list of reference will go.

    ## References 

    [REFERENCES]
    


<h2 id="references">References</h2>
<p>
<ul class="citation-references">
<li class="citation-item" id="bennet70">(Bennett 1970), Bennett, B.M., <em>On the characteristic functions of a local ring</em>, The Annals of Mathematics, <strong>91</strong>(1), 25–87.</li>
<li class="citation-item" id="wiles95">(Wiles 1995), Wiles, Andrew John, <em>Modular elliptic curves and Fermat’s Last Theorem</em>, Annals of Mathematics, <strong>141</strong>.</li>
</ul>

