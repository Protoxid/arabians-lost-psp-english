#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Prologue and Opening (op1.ks) Complete Localization.
Generates fully translated, validated scenario records for pro_name1..3, pro_skip, and op1.ks.
Enforces strict 18-char word-wrapped dialogue formatting to eliminate word-cutting and window overflow.
"""

import os
import sys
import json
import re

sys.path.insert(0, os.path.abspath('.'))
from tools.validate import validate_translation_entry
from tools.repack import repack_file

# Mapping of all 289 lines of op1.ks + prologue files
PROLOGUE_TRANSLATIONS = {
    "pro_name1.ks:L10:msg": "\"My name is...\"",
    "pro_name1.ks:L15:msg": "First name:[br]Up to 7 letters.[br]Surname is fixed:[br]\"Olazabal\".",
    "pro_name2.ks:L3:msg": "\"[firstname] Olazabal--is this correct?\"",
    "pro_name2.ks:L12:select": "OK",
    "pro_name2.ks:L13:select": "Cancel",
    "pro_name3.ks:L3:msg": "\"My name is...[br][firstname] Olazabal.\"",
    "pro_name3.ks:L14:msg": "\"Signature complete!\"",
    "pro_name3.ks:L19:msg": "\"START: Options.[br]Cross: Return.[br]Don't forget,[br]okay?\"",
    "pro_skip.ks:L4:msg": "Skip the opening movie?",
    "pro_skip.ks:L12:select": "Skip opening.",
    "pro_skip.ks:L13:select": "Do not skip.",
    "op1.ks:L15:msg": "\"...Nnnnnnh...\"",
    "op1.ks:L20:msg": "\"...Mmmmmmh...\"",
    "op1.ks:L25:msg": "\"......[br]...Your hands have stopped moving, Milady.\"",
    "op1.ks:L31:msg": "\"B-But......\"",
    "op1.ks:L36:msg": "\"'But'... what?\"",
    "op1.ks:L41:msg": "\"Because this lock is way too hard!\"",
    "op1.ks:L46:msg": "Not that Lyle is going to let me off the hook.",
    "op1.ks:L51:msg": "I am Princess of[br]Gilkhatar, only[br]daughter of the[br]King, our ruler.",
    "op1.ks:L57:msg": "Save my parents,[br]all are beneath me.[br]Yet in study, Lyle[br]holds upper hand.",
    "op1.ks:L63:msg": "I'm stuck in here[br]since dusk, locked[br]till this chest[br]finally yields.",
    "op1.ks:L69:msg": "He won't even allow me a nap.",
    "op1.ks:L74:msg": "\"I'm so sleepy......\"",
    "op1.ks:L79:msg": "If I stop now, I'll[br]lose my feel.[br]All my effort[br]would be wasted.",
    "op1.ks:L85:msg": "I know that.[br]He drummed it into me in earlier lessons.",
    "op1.ks:L91:msg": "I know, but my mind[br]is dull. Only[br]grumbles fill[br]my head now.",
    "op1.ks:L97:msg": "Lockpicking isn't[br]mere habit; it[br]demands a keen,[br]focused mind.",
    "op1.ks:L102:msg": "Complex locks[br]demand intuition,[br]keen wits, and[br]sharp intellect.",
    "op1.ks:L107:msg": "It is mental work.[br]An exhausted brain[br]cannot crack this[br]tricky lock.",
    "op1.ks:L113:msg": "\"Uggghhh......\"",
    "op1.ks:L118:msg": "\"You're no wizard,[br]Milady. Groaning[br]will not make the[br]lock open.\"",
    "op1.ks:L123:msg": "\"This chest wards[br]spells. Only rogue[br]finesse can open[br]such a lock.\"",
    "op1.ks:L130:msg": "\"......[br]You really despise magic users, Master Lyle.\"",
    "op1.ks:L136:msg": "\"Picking locks with[br]a wand? A vulgar[br]shortcut. I truly[br]despise magic.\"",
    "op1.ks:L142:msg": "\"You don't have to be quite so petty about it.\"",
    "op1.ks:L147:msg": "\"Most chests have[br]traps anyway, so[br]thieves won't be[br]obsolete soon.\"",
    "op1.ks:L152:msg": "\"Besides, magicians are handy for magic traps...\"",
    "op1.ks:L157:msg": "\"I despise them.\"",
    "op1.ks:L162:msg": "\"...Right.\"",
    "op1.ks:L167:msg": "Lyle clearly has no intention of indulging me.",
    "op1.ks:L172:msg": "You demonic tutor.[br]I stick my tongue out at him in my head.",
    "op1.ks:L178:msg": "I'd never dare say[br]it aloud. He's far[br]scarier to me than[br]my own parents.",
    "op1.ks:L184:msg": "\"...Enough chatter.[br]Focus your mind.\"",
    "op1.ks:L190:msg": "\"Thieves pick locks[br]in silence. Bad[br]habits make you[br]murmur on a heist.\"",
    "op1.ks:L196:msg": "\"Approach every practice as if your life depends on it.\"",
    "op1.ks:L201:msg": "\"A job...?[br]You don't really plan to send me thieving?!\"",
    "op1.ks:L207:msg": "\"I have no intention of doing that...!\"",
    "op1.ks:L212:msg": "\"Do you claim my[br]lessons need less[br]than your full[br]dedication?\"",
    "op1.ks:L217:msg": "\"N-No, not that![br]This lock is so[br]brutal, I must give[br]it everything!\"",
    "op1.ks:L224:msg": "\"Then give it your all.\"",
    "op1.ks:L229:msg": "\"Even at my best,[br]it's impossible...![br]This lock is way[br]too hard!\"",
    "op1.ks:L235:msg": "\"The keyway is too[br]complex! Crossing[br]pins inside is[br]absurd...!\"",
    "op1.ks:L241:msg": "\"You simply lack willpower.[br]Apply yourself more earnestly.\"",
    "op1.ks:L247:msg": "\"I've tried since[br]last night! If I[br]can't by now, it's[br]truly impossible!\"",
    "op1.ks:L253:msg": "\"You can do it.\"",
    "op1.ks:L258:msg": "Lyle cuts off every single one of my complaints.",
    "op1.ks:L263:msg": "He infuriates me,[br]yet stirs my pride.[br]When he's so sure,[br]I must succeed.",
    "op1.ks:L269:msg": "Fake tears won't[br]sway him at all.[br]I just have to[br]pick this lock.",
    "op1.ks:L276:msg": "\"Fine, fine, I'll do it!\"",
    "op1.ks:L281:msg": "\"Good. Less whining[br]and more picking.[br]Keep quiet and move[br]your hands.\"",
    "op1.ks:L287:msg": "The moment I get motivated, the cold lecture returns.",
    "op1.ks:L292:msg": "\"You can do it.[br]I know you can.\"",
    "op1.ks:L298:msg": "And then he follows it with gentle encouragement.",
    "op1.ks:L303:msg": "\"......[br]...You're an absolute master of carrot and stick.\"",
    "op1.ks:L309:msg": "\"It is my profession, after all.\"",
    "op1.ks:L314:msg": "\"I suppose so...\"",
    "op1.ks:L319:msg": "Lyle does his job.[br]As his pupil, I[br]must do my duty[br]as well.",
    "op1.ks:L325:msg": "Gathering what little focus I have left, I face the lock.",
    "op1.ks:L351:msg": "Click, clatter......",
    "op1.ks:L362:msg": "\"......\"",
    "op1.ks:L373:msg": "\"......\"",
    "op1.ks:L384:msg": "\"......\"",
    "op1.ks:L389:msg": "\"......Ah.[br]I see it now...!\"",
    "op1.ks:L401:msg": "\"...If I rotate the cylinder here......\"",
    "op1.ks:L413:msg": "\"Like this...!\"",
    "op1.ks:L427:msg": "With a sharp metallic snap, the chest springs open.",
    "op1.ks:L432:msg": "\"I did it![br]It opened...!\"",
    "op1.ks:L438:msg": "\"I did it, I did it!!![br]This was a top-tier chest, wasn't it?\"",
    "op1.ks:L444:msg": "\"Isn't that incredible?[br]I'm amazing, right?[br]Right?!\"",
    "op1.ks:L451:msg": "I strained hard and[br]took so long... The[br]relief makes me[br]giddy with joy.",
    "op1.ks:L457:msg": "Coupled with sleep deprivation, my energy spikes.",
    "op1.ks:L462:msg": "I fought all night.[br]It took forever,[br]yet surely I earned[br]some praise!",
    "op1.ks:L469:msg": "I turn to Lyle; he[br]looks astonished.[br]Had he secretly[br]given up on me?",
    "op1.ks:L475:msg": "Then, a slow, gentle smile spreads across his face.",
    "op1.ks:L483:msg": "\"Magnificent!\"",
    "op1.ks:L488:msg": "\"Hehe, impressive,[br]right? Wasn't I[br]amazing? Come on,[br]wasn't I?!\"",
    "op1.ks:L494:msg": "Riding high on an all-nighter and victory, I boast.",
    "op1.ks:L500:msg": "\"Yes, truly impressive.[br]Milady, you were remarkable.\"",
    "op1.ks:L507:msg": "\"I am in awe.[br]I take my hat off to you.\"",
    "op1.ks:L513:msg": "\"...Huh?\"",
    "op1.ks:L518:msg": "Lyle praising me?[br]Usually compliments[br]come laced with[br]stinging barbs.",
    "op1.ks:L524:msg": "Carrot and stick at[br]once. My tutor[br]never lets me get[br]carried away.",
    "op1.ks:L531:msg": "\"You have a gift.[br]You carry the blood[br]of the Thief King[br]after all.\"",
    "op1.ks:L537:msg": "\"......?\"",
    "op1.ks:L542:msg": "\"What's with the sudden flattery?[br]You're laying it on awfully thick.\"",
    "op1.ks:L548:msg": "I can't help wondering if there's an ulterior motive.",
    "op1.ks:L554:msg": "\"Tutoring is a service profession, Milady.\"",
    "op1.ks:L560:msg": "\"Yet today I am genuinely humbled.[br]Your technique was flawless.\"",
    "op1.ks:L572:msg": "\"...You creep me out.[br]Since when do you[br]compliment me like[br]this?\"",
    "op1.ks:L578:msg": "\"You speak as though I were some cold-blooded fiend.\"",
    "op1.ks:L583:msg": "\"...Consider it a special bonus today.[br]You did splendidly.\"",
    "op1.ks:L589:msg": "It's not my first[br]pat on the head.[br]Nor is his praise[br]unprecedented.",
    "op1.ks:L595:msg": "Though there is always a catch.",
    "op1.ks:L600:msg": "Pure praise feels[br]so strange... It[br]makes me happy, but[br]also uneasy.",
    "op1.ks:L606:msg": "\"You're a hardworking, cold-blooded fiend, right?\"",
    "op1.ks:L611:msg": "\"Hardworking...?[br]I merely fulfill my duties to earn my wage.\"",
    "op1.ks:L617:msg": "\"Teaching you is so[br]entertaining... If[br]I pushed too hard,[br]blame yourself.\"",
    "op1.ks:L623:msg": "\"Too hard? It was pure Spartan discipline...\"",
    "op1.ks:L628:msg": "Many times I swore[br]he was a demon.[br]Lyle was never a[br]gentle teacher.",
    "op1.ks:L634:msg": "He invested so much effort that I wished he'd slack off.",
    "op1.ks:L639:msg": "\"I am not easily[br]passionate, yet you[br]were a pupil worth[br]pushing hard.\"",
    "op1.ks:L645:msg": "\"When I took this[br]post, I never knew[br]I would become so[br]zealous a tutor.\"",
    "op1.ks:L650:msg": "\"I meant to do the[br]bare minimum and get[br]by, but you proved[br]me wrong.\"",
    "op1.ks:L655:msg": "\"In the best possible way, of course.\"",
    "op1.ks:L660:msg": "\"......\"",
    "op1.ks:L665:msg": "\"...Master Lyle?[br]You make it sound like...\"",
    "op1.ks:L671:msg": "Like this is the[br]end of the road.[br]A farewell talk[br]with my tutor.",
    "op1.ks:L677:msg": "Was that chest truly such a high-level test?",
    "op1.ks:L682:msg": "A sudden pang of anxiety grips me.",
    "op1.ks:L687:msg": "Lyle is strict, but I wouldn't know what to do without him.",
    "op1.ks:L692:msg": "I spent most days[br]with Lyle; I never[br]imagined those days[br]would ever end.",
    "op1.ks:L697:msg": "\"However, Milady, you have zero practical experience.\"",
    "op1.ks:L702:msg": "\"You have master[br]talent, but zero[br]experience: level 1[br]all the same.\"",
    "op1.ks:L707:msg": "\"Your rogue skills[br]are supreme, yet[br]the weakest monster[br]could kill you.\"",
    "op1.ks:L712:msg": "\"Don't you find that terribly tragic?\"",
    "op1.ks:L717:msg": "\"......\"",
    "op1.ks:L722:msg": "\"...Not in the least.\"",
    "op1.ks:L727:msg": "Talent or not, I[br]won't use it. I've[br]no desire to be a[br]master thief.",
    "op1.ks:L733:msg": "\"Listen, Master Lyle...[br]I never asked for this kind of talent...\"",
    "op1.ks:L739:msg": "\"I told you before,[br]didn't I? I won't[br]use rogue skills[br]in the field.\"",
    "op1.ks:L745:msg": "\"Do you truly intend to let your gifts rot away?\"",
    "op1.ks:L750:msg": "\"Stealing isn't the[br]only way. Hunting[br]monsters alone will[br]raise your level.\"",
    "op1.ks:L756:msg": "\"Letting them sit[br]idle is fine. If I[br]never need them, so[br]much the better.\"",
    "op1.ks:L762:msg": "\"Rather than an elite thief... I just want to be normal.\"",
    "op1.ks:L768:msg": "\"...Normal, you say?\"",
    "op1.ks:L773:msg": "\"Yes. An ordinary, normal person.\"",
    "op1.ks:L778:msg": "\"You always said[br]so... It seems your[br]heart has not[br]changed at all.\"",
    "op1.ks:L784:msg": "\"A common citizen?[br]Apprentice to an[br]assassin, or dwell[br]in the slums???\"",
    "op1.ks:L790:msg": "\"If you fancy becoming a pickpocket, I don't advise it.\"",
    "op1.ks:L795:msg": "\"Locals have sharp[br]skills and bad[br]tempers. The risk[br]is far too high.\"",
    "op1.ks:L800:msg": "\"No, no, that's not it...!\"",
    "op1.ks:L805:msg": "\"A merchant then?[br]I know smugglers,[br]though that needs[br]different skills.\"",
    "op1.ks:L811:msg": "\"...Shall I revise your study curriculum?\"",
    "op1.ks:L816:msg": "\"[f size=\"150\"]NO![/f][br]Not THAT kind of 'normal' for Gilkhatar...!\"",
    "op1.ks:L822:msg": "\"I've told you this before![br]Don't you remember?\"",
    "op1.ks:L828:msg": "His 'normal' fits[br]Gilkhatar well.[br]In that sense, Lyle[br]is quite right.",
    "op1.ks:L833:msg": "But I want a normal that exists beyond our borders.",
    "op1.ks:L838:msg": "\"You have never specified what profession you desire.\"",
    "op1.ks:L843:msg": "\"I want a normal that isn't like Gilkhatar.\"",
    "op1.ks:L848:msg": "\"Then be specific.\"",
    "op1.ks:L853:msg": "\"...Like farming.\"",
    "op1.ks:L858:msg": "\"Far... ming...?\"",
    "op1.ks:L863:msg": "Lyle tilts his head, pondering the word.",
    "op1.ks:L868:msg": "\"Far... ming......\"",
    "op1.ks:L873:msg": "He genuinely cannot comprehend what I mean.",
    "op1.ks:L878:msg": "He isn't mocking me.[br]The concept is utterly foreign in Gilkhatar.",
    "op1.ks:L884:msg": "Watching him struggle makes me feel embarrassed.",
    "op1.ks:L889:msg": "\"Far... ming... Agriculture... Farming...?\"",
    "op1.ks:L894:msg": "He mutters in dead earnest.[br]He is so serious I can't even tease him.",
    "op1.ks:L902:msg": "\"...Farming...[br][f size=\\\"150\\\"]Farming?![/f][br]Do you mean tilling[br]soil for crops?!\"",
    "op1.ks:L908:msg": "\"Yes... exactly that.[br]Unbelievable as it sounds, farming.\"",
    "op1.ks:L914:msg": "At least he finally figured it out.",
    "op1.ks:L919:msg": "His shock is only[br]natural. Gilkhatar[br]is a harsh desert[br]realm after all.",
    "op1.ks:L925:msg": "Our climate makes[br]farming impossible,[br]so almost no[br]farmers exist here.",
    "op1.ks:L930:msg": "Farming requires[br]rich soil, and good[br]land is nearly null[br]in Gilkhatar.",
    "op1.ks:L935:msg": "That is precisely[br]why Gilkhatar grew[br]to prey upon the[br]wealth of others.",
    "op1.ks:L940:msg": "\"It need not be[br]farming, but I want[br]an ordinary, honest[br]trade like that.\"",
    "op1.ks:L945:msg": "\"...Farming... Of all things...[br]Farming, really...?\"",
    "op1.ks:L950:msg": "\"I've seen folk run[br]away to avoid dirt,[br]never someone who[br]longed for it.\"",
    "op1.ks:L955:msg": "\"My acquaintances[br]call it dull and[br]mind-numbing, void[br]of any thrill.\"",
    "op1.ks:L960:msg": "\"I want boredom![br]Gilkhatar has far too many thrills!\"",
    "op1.ks:L966:msg": "\"Folk long for what[br]they lack, yet your[br]view is peculiar,[br]Milady.\"",
    "op1.ks:L971:msg": "\"Farming here is[br]harder than being a[br]master thief. No[br]one would try it.\"",
    "op1.ks:L977:msg": "\"A commoner might consider emigrating, but...\"",
    "op1.ks:L982:msg": "\"......[br]Pardon me, but for[br]your royal station,[br]it is impossible.\"",
    "op1.ks:L988:msg": "Lyle seemed taken[br]aback, but soon[br]declared it flatly[br]impossible.",
    "op1.ks:L995:msg": "\"I know that.\"",
    "op1.ks:L1000:msg": "I readily concede the point.",
    "op1.ks:L1005:msg": "I know a royal[br]can't be a peasant.[br]I can barely even[br]leave the capital.",
    "op1.ks:L1011:msg": "\"I know a normal[br]life is impossible[br]given the royal[br]cradle I was born.\"",
    "op1.ks:L1017:msg": "In that sense, I[br]gave up already.[br]This is my greatest[br]compromise.",
    "op1.ks:L1023:msg": "Instead, I have a far more tangible, realistic hope.",
    "op1.ks:L1028:msg": "\"......\"",
    "op1.ks:L1033:msg": "\"Lyle, did your leg[br]end your journey?[br]Would you stay here[br]without injury?\"",
    "op1.ks:L1039:msg": "Lyle was born here,[br]yet different. He[br]once wandered the[br]whole world.",
    "op1.ks:L1045:msg": "He never stayed put[br]till hurt. Family[br]ties got him tested[br]for royal tutor.",
    "op1.ks:L1051:msg": "Which led to our[br]first meeting. In[br]the beginning, I[br]gave him trouble.",
    "op1.ks:L1057:msg": "...This really feels like a parting scene. Bad omen.",
    "op1.ks:L1062:msg": "\"If I had never crippled my leg... is that what you ask?\"",
    "op1.ks:L1067:msg": "\"......\"",
    "op1.ks:L1072:msg": "\"...Even so, I would have returned eventually.\"",
    "op1.ks:L1077:msg": "\"This land suits me.[br]With power, anyone[br]is welcome in[br]Gilkhatar.\"",
    "op1.ks:L1083:msg": "\"I see......\"",
    "op1.ks:L1088:msg": "\"Wandering felt[br]free, yet the only[br]home I longed for[br]was Gilkhatar.\"",
    "op1.ks:L1094:msg": "\"...Abnormal as it[br]is, I am unusual[br]too, so nowhere[br]suits me better.\"",
    "op1.ks:L1100:msg": "\"...I love it too.[br]I am proud to have[br]been born its[br]princess.\"",
    "op1.ks:L1106:msg": "Its wild nature[br]puts me at ease.[br]I don't seek normal[br]out of hatred.",
    "op1.ks:L1112:msg": "Gilkhatar has virtues only its people can understand.",
    "op1.ks:L1117:msg": "Life would be far[br]simpler if born in[br]lush Grimond, realm[br]of agriculture.",
    "op1.ks:L1122:msg": "I wished to move[br]where all are[br]ordinary, but know[br]I never can.",
    "op1.ks:L1127:msg": "Beyond practical barriers, I am a child of Gilkhatar.",
    "op1.ks:L1132:msg": "\"Still, I want to[br]be normal--to love[br]normally, and wed[br]with genuine love!\"",
    "op1.ks:L1138:msg": "\"That is the normal life I yearn for.\"",
    "op1.ks:L1143:msg": "\"...A remarkably modest dream.\"",
    "op1.ks:L1148:msg": "\"Feminine, wouldn't you say?\"",
    "op1.ks:L1153:msg": "\"A modest dream,[br]yet hardest of all.[br]Feminine, but not[br]very princessly.\"",
    "op1.ks:L1159:msg": "A complicated expression crosses Lyle's face.",
    "op1.ks:L1165:msg": "I gently close my eyes.",
    "op1.ks:L1170:msg": "\"If I cannot be normal, at least let my marriage be.\"",
    "op1.ks:L1175:msg": "At my age, suitors[br]flood the palace.[br]Every offer is a[br]political match.",
    "op1.ks:L1181:msg": "Refusing them took effort, yet I turned down every one.",
    "op1.ks:L1186:msg": "\"Milady......\"",
    "op1.ks:L1191:msg": "\"......\"",
    "op1.ks:L1196:msg": "\"...How hopelessly selfish.\"",
    "op1.ks:L1201:msg": "Hearing him brand me a hopeless pupil stings a little.",
    "op1.ks:L1206:msg": "After years of tutoring, I dread disappointing him.",
    "op1.ks:L1211:msg": "\"Splendid matches,[br]yet you declined[br]all for the sake[br]of sweet romance.\"",
    "op1.ks:L1217:msg": "\"With your rank,[br]marrying a foreign[br]prince is vastly[br]more attainable.\"",
    "op1.ks:L1222:msg": "\"Where is the dream in that?\"",
    "op1.ks:L1227:msg": "Normal girls dream[br]of princes, but I[br]sadly do not fit[br]that sweet mold.",
    "op1.ks:L1232:msg": "Marrying a prince[br]is an everyday[br]reality for me; no[br]romance in that.",
    "op1.ks:L1237:msg": "Being royal, I know[br]what lies beneath.[br]Princes hold no[br]mystery for me.",
    "op1.ks:L1242:msg": "For someone in my[br]station, marrying[br]for love is a far[br]steeper climb.",
    "op1.ks:L1247:msg": "\"I know I'm not an[br]ordinary maiden.[br]That's why I want[br]my marriage to be.\"",
    "op1.ks:L1253:msg": "\"Is that really such an extravagant wish?\"",
    "op1.ks:L1258:msg": "\"A simple wish for[br]common folk, yet a[br]sheer luxury for a[br]royal princess.\"",
    "op1.ks:L1263:msg": "\"...Could you not foster love after the wedding?\"",
    "op1.ks:L1268:msg": "\"Arranged marriages[br]need not be grim.[br]Affection can grow[br]after the wedding.\"",
    "op1.ks:L1274:msg": "\"With a stranger?[br]Hoping for love[br]after marriage is[br]pure foolishness.\"",
    "op1.ks:L1280:msg": "Hoping to click with a stranger is pure luck.",
    "op1.ks:L1285:msg": "Once wed, there's[br]no escape. Testing[br]for love after vows[br]isn't normal.",
    "op1.ks:L1291:msg": "Normal folk love[br]before marriage.[br]Selfish or not,[br]I won't give in.",
    "op1.ks:L1297:msg": "\"...The odds are[br]slim as roulette,[br]barely above zero[br]at best.\"",
    "op1.ks:L1303:msg": "\"Do I strike you as such a starry-eyed optimist?\"",
    "op1.ks:L1308:msg": "\"......\"",
    "op1.ks:L1313:msg": "\"......*sigh*\"",
    "op1.ks:L1318:msg": "Lyle exhales a deep, heavy sigh.",
    "op1.ks:L1323:msg": "I don't mean to trouble him.[br]Yet I must make my intentions clear.",
    "op1.ks:L1329:msg": "Lyle reports to my[br]parents. Through[br]him, my wishes can[br]reach them.",
    "op1.ks:L1335:msg": "\"Father wed for[br]love, didn't he?[br]Then surely I have[br]that right too!\"",
    "op1.ks:L1340:msg": "I sounded harsh,[br]yet Lyle isn't to[br]blame. My anger[br]is with my folks.",
    "op1.ks:L1346:msg": "\"...Is there someone[br]you favor? Still[br]seeing that former[br]paramour?\"",
    "op1.ks:L1352:msg": "\"You're the one who sabotaged that, remember?\"",
    "op1.ks:L1357:msg": "\"We ended long ago.[br]I don't have anyone in mind right now.\"",
    "op1.ks:L1363:msg": "\"That's why! I want[br]to find the one[br]person who truly[br]matters to me.\"",
    "op1.ks:L1369:msg": "Once betrothed or wed, that possibility dies forever.",
    "op1.ks:L1374:msg": "\"......\"",
    "op1.ks:L1379:msg": "\"Still, why not[br]raise your level?[br]It has nothing to[br]do with romance.\"",
    "op1.ks:L1385:msg": "\"It has everything to do with it!\"",
    "op1.ks:L1390:msg": "\"I want a normal[br]romance! If I'm[br]less normal, love[br]drifts further!\"",
    "op1.ks:L1396:msg": "\"...You studied so[br]well, I thought[br]you'd step up in[br]spite of protests.\"",
    "op1.ks:L1401:msg": "\"You did not idle;[br]you worked hard.[br]Ending it before it[br]blooms is a waste.\"",
    "op1.ks:L1407:msg": "Lyle looks genuinely reluctant to accept it.",
    "op1.ks:L1412:msg": "I get his grief:[br]his star pupil[br]worked hard, only[br]to skip the test.",
    "op1.ks:L1418:msg": "Drilled so hard, I[br]would level fast in[br]combat. No wonder[br]he feels it waste.",
    "op1.ks:L1424:msg": "\"If your devotion was my fault, then my effort was yours.\"",
    "op1.ks:L1429:msg": "I feel pity too. I[br]never intended to[br]become so skilled[br]at thievery.",
    "op1.ks:L1436:msg": "When I open my eyes, our gazes meet.[br]I don't look away.",
    "op1.ks:L1442:msg": "\"You teach too[br]well! You got me[br]hooked, so I never[br]could slack off.\"",
    "op1.ks:L1448:msg": "\"I meant to ditch[br]and get you fired.[br]Instead, I was the[br]one surprised!\"",
    "op1.ks:L1454:msg": "\"...Such sweet words from my pupil.\"",
    "op1.ks:L1468:msg": "Lyle reaches out and ruffles my hair vigorously.",
    "op1.ks:L1473:msg": "...Is he flustered?[br]He is showing me rare expressions today.",
    "op1.ks:L1479:msg": "\"There is no greater honor for a teacher.[br]You are my pride and joy.\"",
    "op1.ks:L1485:msg": "\"...Master Lyle, you aren't stepping down, are you?\"",
    "op1.ks:L1490:msg": "Such gentleness[br]makes me wary. He[br]is never quite[br]this soft.",
    "op1.ks:L1496:msg": "He is treating this like a graduation ceremony.",
    "op1.ks:L1501:msg": "\"Nobody told me you were resigning!\"",
    "op1.ks:L1506:msg": "\"I never said I was resigning.\"",
    "op1.ks:L1511:msg": "\"Why jump to dark[br]thoughts? When praised,[br]accept it with[br]grace.\"",
    "op1.ks:L1517:msg": "\"Because I'm not a good student!\"",
    "op1.ks:L1522:msg": "\"I'm wasting all[br]you taught me. I've[br]done nothing to[br]earn such praise!\"",
    "op1.ks:L1528:msg": "\"So you do realize it.[br]And yet you still refuse to raise your level?\"",
    "op1.ks:L1534:msg": "\"......\"",
    "op1.ks:L1539:msg": "\"I feel awful about letting your teaching go to waste, but...\"",
    "op1.ks:L1544:msg": "\"Indeed. You are a dreadful pupil.\"",
    "op1.ks:L1549:msg": "\"...You didn't have to agree so quickly!\"",
    "op1.ks:L1554:msg": "\"Being wicked suits you fine.\"",
    "op1.ks:L1572:msg": "With that, Lyle ruffles my hair even harder.",
    "op1.ks:L1577:msg": "Hair isn't on his[br]mind... No mirror,[br]yet I know what a[br]mess my head is.",
    "op1.ks:L1583:msg": "\"This is a den of[br]crime; you're the[br]princess. Be as[br]evil as you wish.\"",
    "op1.ks:L1589:msg": "\"I shall support[br]you every step. I am[br]your royal tutor,[br]after all.\"",
    "op1.ks:L1595:msg": "\"When I specifically said I wanted to be normal...\"",
    "op1.ks:L1600:msg": "I wished to whine,[br]yet felt relief.[br]Lyle has no intent[br]of leaving.",
    "op1.ks:L1606:msg": "\"Encouraging your student to be wicked?[br]You fail as an educator.\"",
    "op1.ks:L1611:msg": "\"And you, Milady, are hardly a model student.\"",
    "op1.ks:L1616:msg": "With a smirk, Lyle musses my hair yet again.",
    "op1.ks:L1632:msg": "\"......\"",
    "op1.ks:L1637:msg": "\"...[f size=\"150\"]Stop it, you'll make me go bald![/f]\""
}

def reflow_text(text: str, max_line_len: int = 18) -> str:
    """
    Safely wraps English dialogue text using [br] tags at whole word boundaries.
    Ensures no word is sliced across line breaks and line length never exceeds safe limits.
    """
    # 1. If the text already has manual [br] and all lines are <= 19 chars, preserve it
    existing_lines = text.split('[br]')
    clean_lines = [re.sub(r'\[[^\]]+\]', '', l).strip() for l in existing_lines]
    if all(len(l) <= 19 for l in clean_lines) and len(existing_lines) <= 4:
        return text

    # 2. Otherwise reflow cleanly across word boundaries
    clean = re.sub(r'\[br\]', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    words = clean.split(' ')
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        w_vis = len(re.sub(r'\[[^\]]+\]', '', w))
        test_len = cur_len + (1 if cur else 0) + w_vis
        if cur and test_len > max_line_len:
            lines.append(' '.join(cur))
            cur = [w]
            cur_len = w_vis
        else:
            cur.append(w)
            cur_len = test_len
    if cur:
        lines.append(' '.join(cur))
        
    return '[br]'.join(lines)

def generate_prologue_translations():
    os.makedirs('translations/working', exist_ok=True)
    os.makedirs('translations/reviewed', exist_ok=True)
    
    # 1. Load source scenario_all.jsonl
    source_records = {}
    with open('translations/source/scenario_all.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            source_records[d['id']] = d

    # 2. Match and validate
    output_records = []
    validation_errors = []
    
    for rid, raw_en in PROLOGUE_TRANSLATIONS.items():
        src_entry = source_records.get(rid)
        if not src_entry:
            print(f"Warning: Record {rid} not found in source database!")
            continue
            
        jp_text = src_entry['japanese']
        en_text = reflow_text(raw_en, max_line_len=18)
        errs = validate_translation_entry(rid, jp_text, en_text)
        if errs:
            validation_errors.append((rid, errs))
            
        record = dict(src_entry)
        record['english'] = en_text
        record['translation_status'] = 'reviewed'
        output_records.append(record)

    print(f"Processed {len(output_records)} records.")
    if validation_errors:
        print(f"Found {len(validation_errors)} validation errors:")
        for rid, errs in validation_errors:
            print(f"  [{rid}] {errs}")
        sys.exit(1)
        
    # 3. Write out to translations/working and translations/reviewed
    for out_path in ['translations/working/prologue_translated.jsonl', 'translations/reviewed/prologue_translated.jsonl']:
        with open(out_path, 'w', encoding='utf-8') as f:
            for r in output_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"Successfully generated {out_path} with {len(output_records)} validated lines.")
    
    # 4. Verify repacking of all affected scenario files
    files_affected = set(r['source_file'] for r in output_records)
    print(f"\nVerifying repacking for {len(files_affected)} scenario files:")
    for sf in sorted(files_affected):
        sf_trans = {r['id']: r['english'] for r in output_records if r['source_file'] == sf}
        src_path = os.path.join('extracted/data_cpk/scenario', sf)
        repacked = repack_file(src_path, sf_trans, sf)
        repacked.encode('cp932')
        print(f"  {sf}: Repacked and verified CP932 encoding ({len(repacked)} chars, {len(sf_trans)} translated lines)")
        
if __name__ == '__main__':
    generate_prologue_translations()
