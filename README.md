# Happy Farmer #

## Вводная часть

***О скрипте.*** Скрипт создан для абуза @Litecoin_click_bot в Telegram.
Если приложить немного усилий, его можно адаптировать под работу с 
@BTC_click_bot, @BCH_click_bot, @Doge_click_bot. Но, как я убедился на
практике, это бесполезно. Нормально платят только в @Litecoin_click_bot.

***Архитектура проекта.*** В общих чертах расскажу об архитектуре поекта. 
Как вы могли заметить, весь код разбит на несколько файлов: ```start.py, 
main.py, func.py```

```start.py``` запускает работу скрипта и перезапускает его, если он по
каким-либо причинам упал.   
```main.py``` содержит в себе функцию-контроллер скрипта. С помощью этой функции
протзователь осуществляет работу со скриптом: добавляет необходимые для 
рыботы данные в бд, запускает работу скрипта и др.  
```func.py``` - это "мозг" скрипта. В файле находятся все функции, необходимые 
для абуза @Litecoin_click_bot.  

***Обратная связь.*** Есть какие-нибудь предложения по улучшению проекта? Есть
замечани по коду? Возникли вопросы? Пишите мне в VK: https://vk.com/mtchuikov
или Telegram: https://t.me/mtchuikov.

***Поддержать автора.***  
BNB (bep20): 0xa4ca77291e6a7532d527b0d3efbe265ae4eceec0  
TRX: TTdXB7RbydKQpxs3wXJx4GBm9r9EqKuBaW  
LTC: Lgp4w1ubkAgcQEVVBSiAN788FUHmZyh5c9  
Qiwi nickname: MTCHUIKOV

## Мануал по работе со скриптом

***Предварительная подготовка.***     
```Шаг 1.``` Устанавливаем интерпритатор Python.  
Инструкция по установке Python https://python-scripts.com/install-python  
```Шаг 2.``` Так же понадобится PIP (python installer packagea).   
Инструкция по сутановке PIP: https://pythonru.com/baza-znanij/ustanovka-pip-dlja-python-i-bazovye-komandy  

What if there was a common format for the benefit of producers and consumers?

A *common readme* for node modules.

This can save everybody time by adhering to 4 principles:

1. **No lock in.** No special formats or tooling; run `common-readme` once for
   pure vanilla markdown.
2. **No surprises.** Pull as many details out of `package.json` -- like name,
   description, and license -- as possible. No time wasted on configuration.
3. **Cognitive funnelling.** Start with the most general information at the top
   (Name, Description, Examples) and if the reader maintains interest, narrow
   down to specifics (API, Installation). This makes it easy for readers to
   "short circuit" and continue the hunt for the right module elsewhere without
   wasting time delving into unnecessary details.
4. **Consistency.** Your brain can scan a document much faster when it can
   anticipate its structure.

## Common format

common-readme operates on the principle of *cognitive funneling*.

> Ideally, someone who's slightly familiar with your module should be able to
> refresh their memory without hitting "page down".  As your reader continues
> through the document, they should receive a progressively greater amount of
> knowledge. -- `perlmodstyle`

Here are some READMEs generated using common-readme:

- [`collide-2d-aabb-aabb`](https://github.com/noffle/collide-2d-aabb-aabb)
- [`goertzel`](https://github.com/noffle/goertzel)
- [`twitter-kv`](https://github.com/noffle/twitter-kv)

*([Submit a pull request](https://github.com/noffle/common-readme/pulls) and add
yours here!)*

## Usage

With [npm](https://npmjs.org/) installed, run

    $ npm install -g common-readme

`common-readme` is a command line program. You run it when you've started a new
module that has a `package.json` set up.

When run, a brand new README is generated and written to your terminal. You can
redirect this to `README.md` and use it as a basis for your new module.

    $ common-readme > README.md

This brand new readme will be automatically populated with values from
`package.json` such as `name`, `description`, and `license`. Stub sections will
be created for everything else (Usage, API, etc), ready for you to fill in.

## Why?

This isn't a crazy new idea. Other ecosystems like [Perl's
CPAN](http://perldoc.perl.org/perlmodstyle.html) have been benefiting from a
common readme format for years. Furthermore:

1. The node community is powered by us people and the modules we share. It's our
   documentation that links us together. Our README is the first thing
   developers see and it should be maximally effective at communicating its
   purpose and function.

2. There is much wisdom to be found from the many developers who have written
   many many modules. Common readme aims to distill that experience into a
   common format that stands to benefit us all; especially newer developers!

3. Writing the same boilerplate is a waste of every author's time -- we might as
   well generate the common pieces and let the author focus on the content.

4. Scanning through modules on npm is a part of every node developer's regular
   development cycle. Having a consistent format lets the brain focus on content
   instead of structure.

## The Art of README

For even more background, wisdom, and ideas, take a look at the article that
inspired common-readme:

- [*Art of README*](https://github.com/noffle/art-of-readme).

## Install

With [npm](https://npmjs.org/) installed, run

```shell
npm install -g common-readme
```

You can now execute the `common-readme` command.

## Acknowledgments

A standard readme format for the Node community isn't a new idea. Inspiration
came from many conversations and unrealized efforts in the community:

- <https://github.com/feross/standard/issues/141>
- [richardlitt/standard-readme](https://github.com/RichardLitt/readme-standard)
- [zwei/standard-readme](https://github.com/zcei/standard-readme)

This, in addition to my own experiences evaluating hundreds of node modules and
their READMEs.

I was partly inspired by the audacity of the honey-badger-don't-care efforts of
[standard](https://github.com/feross/standard).

I also did a great deal of Perl archaeology -- it turns out the monks of the
Perl community already did much of the hard work of [figuring out great
READMEs](http://perldoc.perl.org/perlmodstyle.html) and the wisdom around small
module development well over a decade ago.

Thanks to @mafintosh, @andrewosh, and @feross for many long conversations about
readmes and Node.

## See Also

READMEs love [`readme`](https://www.npmjs.com/package/readme)!

## License

ISC
