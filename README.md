# Machine-Translation-with-CRFs
Project 2 of [NLP2](https://uva-slpl.github.io/nlp2/). Read the [project description](readings/project2.pdf) or the [paper](readings/Blunsom08.pdf) that partly inspired it.

## How-to

* Use `save-parses.py` to save the parse-forest of a number of sentence pairs of a corpus. In `translations` you can set `k` and `null` to control how many translations (`k`) and insertions (`null`) to make. Set the size of the corpus in `read_data` and the maximal sentence length just below.

* Use `train.py` to load these parses and train on them. Specify how many sentences you load in the list comprehension in line 11. You can pre-train a `w` and save this. Then reload this one each time you train (redo this whenever you reload new parses!). Use sgd_minibatches when training on a large corpus. 

* Use `predict.py` to load in a trained weights vector `w` and some `parses` in the right format, and predict the best translations (viterbi and sampled). Write these to a prediction .txt file in the folder `predict`. These can be used to compute BLEU scores.

* Note that we're using a hack to prevent huge values in the weight vector: in SGD the optional parameter scale_weight can be set to any integer `k`. Then all values in the weight vector are scaled so that none exceed `10**k`.

* SGD has been updated so that we scale the learning rate each time we make a weight-vector update (i.e. each minibatch). See section 5.2 of [this paper](readings/bottou-sgd-tricks-2012.pdf) on SGD-tricks. This introduces a new hyperparameter `lmbda` which controls the rate of scaling. We now start with a high learning rate of around 1 to 10, and let the formula scale this down.

## The parses

Let's train with *three types of parses*: small sentences of length 10, with only 2 translations (plus `-EPS-`, so 3); small sentences of length 10, with only 4 translations (plus `-EPS-`, so 5); long sentences of length 15, with only 2 translations (plus `-EPS-`, so 3). With the new parallel parser we can now do `max_sents=40000`. See the settings below and the link to the dropbox where they are located.

* `ch_en, en_ch, _, _ = translations(path='data/lexicon', k=3, null=3, remove_punct=True)`
`corpus = read_data(max_sents=40000)`
`corpus = [(ch, en) for ch, en in corpus if len(en.split()) < 10]`. [Link to training parses](https://www.dropbox.com/sh/454l7wo4s69nnls/AADz2kWop6nzbsR04-TUih7ja?dl=0&lst=&preview=eps-40k-ml10-3trans.zip). [Link to dev parses](https://www.dropbox.com/sh/454l7wo4s69nnls/AADz2kWop6nzbsR04-TUih7ja?dl=0&lst=&preview=ml10-3trans.zip).
 
* `ch_en, en_ch, _, _ = translations(path='data/lexicon', k=5, null=5, remove_punct=True)`
`corpus = read_data(max_sents=40000)`
`corpus = [(ch, en) for ch, en in corpus if len(en.split()) < 10].` [Link to training parses](https://www.dropbox.com/sh/454l7wo4s69nnls/AADz2kWop6nzbsR04-TUih7ja?dl=0&lst=&preview=eps-40k-ml10-5trans.zip). [Link to dev parses](https://www.dropbox.com/sh/454l7wo4s69nnls/AADz2kWop6nzbsR04-TUih7ja?dl=0&lst=&preview=ml10-5trans.zip).

* `ch_en, en_ch, _, _ = translations(path='data/lexicon', k=3, null=3, remove_punct=True)`
`corpus = read_data(max_sents=20000)`
`corpus = [(ch, en) for ch, en in corpus if len(en.split()) < 15].`  [Link to training parses](https://www.dropbox.com/sh/454l7wo4s69nnls/AADz2kWop6nzbsR04-TUih7ja?dl=0&lst=&preview=eps-20k.zip). [Link to dev parses](). `TODO`

`Note:` When you select the sentences of a certain length you get a smaller number than 40k! The first example with `<10` gives 28372 parses, but when you put `<15` you will catch more sentences. To make sure that in the final training we can compare the runs for the three different parse-types fairly let's  **only use the parses 0-28k**.

`Note:` Tim has made a parallel version of save-parses! You can now use the branch parallel to check it out for yourself. If you have 4 cores you can simply run `python save-parse.py --num-cores 8` and see the magic of parallel computing unfold in front of your eyes. Warning: expect massive speedup (4x or more) and some beautiful wind-tunnel effects from your desktop/laptop.


## Training schedule

* `DONE` I'm at this moment (Monday 12:42) training on `eps-40k-ml10-3trans` and `eps-40k-ml10-5trans` with [these](prediction/eps-40k-ml10-3trans/screenshot.png) resp. [these](prediction/eps-40k-ml10-5trans/screenshot.png) settings. This will take approximately 12 hours.

* `TODO` I would propose to use the same settings to train on `eps-40k-ml15-3trans`.

* If you want to train on any of the three parses with different settings, please do!

## Trained weights

* One iteration over the whole `eps-40k-ml10-3trans`: [weights](trained-weights/eps-40k-ml10-3trans/trained-1-weights.pkl). See training settings [here](trained-weights/eps-40k-ml10-3trans/screenshot.png).

* One iteration over the whole `eps-40k-ml10-5trans`: [weights](trained-weights/eps-40k-ml10-5trans/trained-1-weights.pkl). See training settings [here](trained-weights/eps-40k-ml10-5trans/screenshot.png).

* `TODO` One iteration over the whole `eps-40k-ml15-3trans`: [weights](trained-weights/eps-40k-ml15-3trans/trained-1-weights.pkl)

## Training-set translations

We have some wonderful training-set translations! The [reference translations](prediction/eps-40k-ml10-3trans/reference.txt) of the training-set.

* [Translations](prediction/eps-40k-ml10-3trans/viterbi-predictions-1.txt) for `eps-40k-ml10-3trans`. BLEU = 4.04.

* [Translations](prediction/eps-40k-ml10-5trans/viterbi-predictions-1.txt) for `eps-40k-ml10-5trans`. BLEU = ... `TODO` (BLEU-script-issues...)

## Dev-set translations

We have obtained the following translations with the above trained weights. See also the [reference translations](prediction/dev/reference.txt) of the dev-set.

* [Translations](prediction/dev/ml10-3trans/viterbi-predictions-1.txt) for `eps-40k-ml10-3trans`. BLEU = ...  `TODO` (BLEU-script-issues...)

* [Translations](prediction/dev/ml10-5trans/viterbi-predictions-1.txt) for `eps-40k-ml10-5trans`. BLEU = ...  `TODO` (BLEU-script-issues...)

## Some notes on training

* Every experiment I've performed so far unequivocally shows that averaging the update of `w` over a minibatch is *bad*. Instead we should update `w` *sentence per sentence*.  ~Use a large batch size. Probably in the range `30-100`. This gives stability to the updates of `w`, since most of the features don't 'fire' for one training example.~ 

* Multiple iterations do not improve anything. I've repeatedly gotten the best results after only 1 epoch. In fact, after the first epoch, nothing much changes, and the change that we do get is almost alway bad, like adding `. i i ` at the end of the sentence after the period which you can see happening [here](prediction/2k/full/viterbi-predictions-1.txt) in the second iteration. I suggest we just use a few (1-4) iterations, and then probably choose the weights we got after the first.

* The choice of learning rate does not matter much. I've tried with many values of `delta_0` ranging from 1-100, and they al practically do the same. I've also tried many values of `lmbda` ranging from 5-0.001, and this also does not have a great deal of influence. However, if we do not use minibatches and update per sentence we should choose a small `lmbda`, just to be sure (otherwise we shrink the learning rate really quickly).

* The regularizer still does not perform as promised: it does not promote small weights. Nor does it give good translations. Basically it's shit. 

* We should stay with the hack! It's just amazing. The precise scale at which we cut does not matter greatly. Probably, we should just keep 1-3. This has worked fine in every experiment so far.
 
* Shuffling is still ok, but as noted above, multiple iterations do not accomplish much, and so shuffle has not much of a function. [Using `shuffle=True` we reshuffle the parses and partition these into new minibatches at each iteration. This drastically improves 'movement' of predicted translation sentences over iterations. Compare the sentences in [shuffle](prediction/2k/shuffle) to those in [no-shuffle](prediction/2k/no-shuffle) and see the difference: the the `no-shuffle` sentences are almost stationary after the first iteration except for some insertions and deletions of 'the'; the `shuffle` sentences on the other continue to change drastically each iteration. I think our best shot is with `shuffle` for this reason: we just need to take this 'movement' behaviour into account (see note below).]

## Some (old) results

See [these translations](prediction/2k/full/viterbi-predictions-0.txt) for our best result so far! This has been achieved by training 1 iteration over 1300 sentences of maximal length 9 parsed with `eps=True` and maximally 3 epsilon insertions, with minibatch size 1, `delta_0=10`, `lmbda=0.01`, `scale_weight=2` and `regularizer=False`. See the [correct translations](prediction/2k/full/reference.txt) for reference. (Also note that later iterations get worse which you can see [here](prediction/2k/full/viterbi-predictions-1.txt).) Lastly: we achieve a BLEU score of 3.44 on these translations (hurray!): `BLEU = 3.44, 49.8/6.2/1.1/0.5 (BP=0.967, ratio=0.968, hyp_len=1222, ref_len=1263)`.

## To-do

* `new!` Parse the Chinese sentences in the development set (~500 sentences) and BLEU-evaluate the trained weights on these. `note:` use the same parse-settings for these dev-sentences as you used for the training-sentences from which you've obtained the weights (not yet 100\% sure why - we'll see).

* Mess around training on different sizes of corpus, with different mini-batch sizes, learning-rates, scale_weights, and regularizers.

* Think about more features. Check `simple_features` for what we already have. Perhaps we need more span features. I added skip-bigram features recently: `le * noir` for the word `chien` in `le chien noir.`, and `chien * -END-` for `.`. 

## Some issues/questions

* The problem with derivations for which the `p(y,d|x) = nan` is this: the weights vector `w`. This *still* occurs, even with the above described hack. It *only* occurs with long sentences though. I think because for a long sentence, the derivation has many edges. And then `sum([estimated_weights[edge] for edge in derrivation])` gets upset, which we use in `join_prob` to compute the  `p(y,d|x)`. NOTE: This is not *really* an issue: we still get Viterbi estimates! We just cannot compute the correct probability.
