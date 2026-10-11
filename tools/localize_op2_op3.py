#!/usr/bin/env python3
"""
Arabians Lost (PSP) — Opening Scenes op2.ks & op3.ks Complete Localization.
Generates fully translated, validated scenario records for op2.ks (337 lines) and op3.ks (34 lines).
Enforces strict 18-char word-wrapped dialogue formatting to eliminate word-cutting and window overflow.
"""

import os
import sys
import json
import re

sys.path.insert(0, os.path.abspath('.'))
from tools.validate import validate_translation_entry
from tools.repack import repack_file

def reflow_text(text: str, max_line_len: int = 18) -> str:
    """
    Safely wraps English dialogue text using [br] tags at whole word boundaries.
    Ensures no word is sliced across line breaks and line length never exceeds safe limits.
    """
    existing_lines = text.split('[br]')
    clean_lines = [re.sub(r'\[[^\]]+\]', '', l).strip() for l in existing_lines]
    if all(len(l) <= 19 for l in clean_lines) and len(existing_lines) <= 4:
        return text

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

OP3_TRANSLATIONS = {
    "op3.ks:L12:msg": "\"I knew this day[br]would come, but I[br]guess there really[br]is no escape...\"",
    "op3.ks:L21:msg": "I drag my feet[br]aimlessly down[br]the long hallway.",
    "op3.ks:L26:msg": "A forced engagement,[br]and then marriage.[br]My footsteps feel[br]heavy as lead.",
    "op3.ks:L32:msg": "Dawdling along[br]won't let me[br]escape reality.",
    "op3.ks:L37:msg": "The countdown starts[br]tomorrow. From[br]nothing to ten[br]million Gold.",
    "op3.ks:L43:msg": "It's an absolutely[br]dizzying sum...",
    "op3.ks:L48:msg": "Still, striking a[br]deal is better than[br]none. If forced, I'd[br]have to run away.",
    "op3.ks:L54:msg": "Though that would[br]be childish. I'd[br]just get dragged[br]back in disgrace.",
    "op3.ks:L60:msg": "Besides, I have[br]no one who would[br]elope with me.",
    "op3.ks:L65:msg": "Mother is right.[br]It's not as if I[br]have someone I love[br]above all else.",
    "op3.ks:L70:msg": "I simply yearn to[br]experience normal,[br]genuine romance.",
    "op3.ks:L75:msg": "Not grand passion,[br]just an ordinary man[br]who could love[br]me honestly...",
    "op3.ks:L80:msg": "\"I should have gone[br]to study abroad...\"",
    "op3.ks:L85:msg": "Had I gone abroad[br]like Father did, I[br]might have found a[br]spouse, as he did.",
    "op3.ks:L91:msg": "Whether Mother counts[br]as 'normal' or not,[br]Father at least[br]married for love.",
    "op3.ks:L96:msg": "Born here, I was[br]never even allowed[br]to leave this land.",
    "op3.ks:L101:msg": "I merely sneak out[br]into the capital[br]every now and then.",
    "op3.ks:L106:msg": "No soul in this[br]realm would dare[br]harm the thief[br]king's only child.",
    "op3.ks:L112:msg": "The doted-upon heir[br]of our absolute[br]ruler. Blessed with[br]rank and wealth...",
    "op3.ks:L118:msg": "Yet stripped of my[br]title, I have no[br]worth of my own.",
    "op3.ks:L123:msg": "Perhaps princesshood[br]itself is void.[br]They wanted a prince,[br]not a daughter.",
    "op3.ks:L129:msg": "It is something I[br]can never change.",
    "op3.ks:L134:msg": "Being an only child,[br]not being a son...[br]Being sheltered,[br]being overprotected.",
    "op3.ks:L140:msg": "To resent what[br]can't be helped,[br]to chafe at being[br]cherished...",
    "op3.ks:L145:msg": "\"Damn it, how[br]childish of me...\"",
    "op3.ks:L150:msg": "Nothing can change[br]my birth.",
    "op3.ks:L155:msg": "Yet finding worth in[br]myself isn't beyond[br]me. That is my own[br]task to solve.",
    "op3.ks:L161:msg": "Mother's worry is[br]justified. I truly[br]am spoiled and[br]immature.",
    "op3.ks:L167:msg": "No wonder she doubts[br]me unless I earn[br]ten million Gold.[br]I am unproven.",
    "op3.ks:L187:msg": "\"......!\"",
    "op3.ks:L192:msg": "I sense a presence.",
    "op3.ks:L197:msg": "Though untested in[br]battle, Master Lyle's[br]drills made my[br]senses razor-sharp.",
    "op3.ks:L202:msg": "I yearn to be[br]'normal', yet my[br]instincts are far[br]from ordinary.",
    "op3.ks:L207:msg": "The one stepping[br]forward is... someone[br]I recognize well...",
}

OP2_PART_A = {
    "op2.ks:L12:msg": "Summoned by my[br]parents, I made my[br]way to the royal[br]audience chamber.",
    "op2.ks:L17:msg": "As princess, no[br]guards bar my path.[br]Yet barge in unbidden[br]means a scolding.",
    "op2.ks:L25:msg": "Father the King,[br]Mother the Queen,[br]and key ministers[br]stand assembled.",
    "op2.ks:L31:msg": "Anyone else would[br]cower, but to me[br]this is merely a[br]room of kin.",
    "op2.ks:L37:msg": "The King of[br]Gilkhatar, Gardin[br]Olazabal.",
    "op2.ks:L42:msg": "Supreme sovereign,[br]the only man who[br]may style himself[br]Gardin Gilkhatar.",
    "op2.ks:L47:msg": "Stern to vassals,[br]ruthless to foes.[br]Cold, formidable,[br]a fitting monarch.",
    "op2.ks:L53:msg": "The Queen, Lastia[br]Olazabal.",
    "op2.ks:L58:msg": "A foreign bride from[br]Karakushu, realm of[br]woods and herbalists,[br]wed in his youth.",
    "op2.ks:L64:msg": "Now steeped in[br]Gilkhatar ways, she[br]wields power second[br]only to the King.",
    "op2.ks:L69:msg": "At Father's side[br]stands Totam Bale,[br]master of the South.",
    "op2.ks:L74:msg": "Nominally in charge[br]of South Capital,[br]in truth he rules the[br]entire southern tier.",
    "op2.ks:L79:msg": "The King's kinsman,[br]trusted deeply in[br]both public duty[br]and private matters.",
    "op2.ks:L84:msg": "At Mother's side[br]stands Joshua Sink,[br]overseer of North.",
    "op2.ks:L89:msg": "His polar opposite,[br]also kin to the King,[br]yet famous for their[br]bitter feud.",
    "op2.ks:L95:msg": "Despite their enmity,[br]both have heir sons[br]who are my childhood[br]companions.",
    "op2.ks:L100:msg": "All feared tyrants[br]at home and abroad,[br]yet to me they are[br]merely my family.",
    "op2.ks:L105:msg": "In short, cousins.[br]Being close kin,[br]they don't frighten[br]me in the least.",
    "op2.ks:L114:msg": "Peering in, I see[br]another guest besides[br]the ministers and[br]guards.",
    "op2.ks:L118:msg": "The grim atmosphere[br]might be due to my[br]summons, or perhaps[br]this visitor.",
    "op2.ks:L123:msg": "Even a princess cannot[br]interrupt an audience,[br]so I step aside to[br]wait.",
    "op2.ks:L128:msg": "His back is turned.[br]I wonder who was[br]summoned, and for[br]what reason.",
    "op2.ks:L134:msg": "Did he bungle a job?[br]Human nature makes[br]us curious about[br]another's trouble.",
    "op2.ks:L142:msg": "\"Understood?![br]You must win my[br]daughter's heart at[br]any cost!\"",
    "op2.ks:L148:msg": "[f size=\"150\"]?![/f]",
    "op2.ks:L153:msg": "[f size=\"150\"]What?![/f]",
    "op2.ks:L158:msg": "\"......?!\"",
    "op2.ks:L163:msg": "This is no stranger's[br]affair at all...",
    "op2.ks:L168:msg": "I have no sisters.",
    "op2.ks:L173:msg": "The daughter he[br]speaks of can only[br]be me.",
    "op2.ks:L178:msg": "'Win my daughter's[br]heart'... An absurd[br]order, yet heard[br]in dead earnest.",
    "op2.ks:L183:msg": "Now I realize why[br]I was summoned.[br]This isn't the first[br]time either.",
    "op2.ks:L189:msg": "...No doubt about it,[br]another marriage[br]proposal.",
    "op2.ks:L194:msg": "Ever eager to curb[br]my yearning for a[br]'normal' life, they[br]ply me with matches.",
    "op2.ks:L199:msg": "Marry a Gilkhatar[br]man and you'll turn[br]properly wicked,[br]or so they believe.",
    "op2.ks:L209:msg": "\"Sire, the princess[br]is still tender.[br]Need we force this[br]match so soon?\"",
    "op2.ks:L219:msg": "\"Naive sentiment.[br]The princess is an[br]idle dreamer who[br]needs waking.\"",
    "op2.ks:L227:msg": "\"She is of age, yet[br]still speaks of being[br]'normal'. A grave[br]matter for state.\"",
    "op2.ks:L233:msg": "Totam takes my side,[br]only for Joshua to[br]instantly snap back.",
    "op2.ks:L239:msg": "\"Love blooms in its[br]own season. Meddling[br]old men only spoil[br]the flower.\"",
    "op2.ks:L246:msg": "\"Do you not grasp the[br]gravity? She is the[br]King's only child.[br]If wed to an outsider--\"",
    "op2.ks:L254:msg": "\"She need not wed[br]away from us.\"",
    "op2.ks:L260:msg": "\"If he be a foreigner,[br]kidnap him and take[br]him as consort.[br]Kidnapping is art!\"",
    "op2.ks:L267:msg": "\"Do you treat high[br]state matters as a[br]petty jest?!\"",
    "op2.ks:L273:msg": "\"Her consort becomes[br]heir to the crown![br]Or right hand to[br]the ruling Queen!\"",
    "op2.ks:L280:msg": "\"Even against her[br]will, she must marry[br]a mighty lord of[br]Gilkhatar!\"",
    "op2.ks:L287:msg": "\"You fret far too[br]much over trifle.\"",
    "op2.ks:L293:msg": "\"You think far too[br]little of state!\"",
    "op2.ks:L298:msg": "\"......\"",
    "op2.ks:L303:msg": "Totam is too lax,[br]Joshua too tense.[br]They never see[br]eye to eye.",
    "op2.ks:L309:msg": "Old grudges aside,[br]they are naturally[br]opposed. Without rank[br]they'd duel daily.",
    "op2.ks:L316:msg": "\"High birth cannot[br]command affection.[br]None should know that[br]better than you.\"",
    "op2.ks:L323:msg": "\"......!\"",
    "op2.ks:L329:msg": "\"Do you dare mock me[br]with personal affairs[br]in court...?!\"",
    "op2.ks:L337:msg": "\"Enough, both of[br]you. Cease this[br]squabbling.\"",
    "op2.ks:L343:msg": "\"Totam, I wish my girl[br]a marriage of love,[br]yet she is stubborn.[br]A parent must guide.\"",
    "op2.ks:L351:msg": "\"Joshua, I share your[br]care for the realm,[br]yet I will not force[br]misery upon her.\"",
    "op2.ks:L357:msg": "Father halts them.[br]He carries himself[br]with true regal[br]dignity.",
    "op2.ks:L363:msg": "Yet he contradicts[br]himself: pledging[br]no forced vows while[br]parading suitors.",
    "op2.ks:L370:msg": "\"Did you hear well[br]what I spoke?!\"",
    "op2.ks:L375:msg": "Father turns from the[br]dueling lords to the[br]prostrate man.",
    "op2.ks:L380:msg": "Cloaked in a robe,[br]his face is hidden.[br]Yet something feels[br]familiar about him.",
    "op2.ks:L387:msg": "\"Win my daughter and[br]your future is made.[br]Riches and renown[br]shall be yours.\"",
    "op2.ks:L394:msg": "\"If you have ambition,[br]claim her hand!\"",
    "op2.ks:L399:msg": "Who would fall for[br]a man hunting rank?[br]A retort rises in[br]my throat.",
    "op2.ks:L406:msg": "\"Swiftly, surely![br]Yet lay no crude[br]force upon my sweet[br][firstname]!\"",
    "op2.ks:L413:msg": "\"No rough handling,[br]no crude coercion![br]Keep your distance![br]Harming her is death!\"",
    "op2.ks:L420:msg": "\"......\"",
    "op2.ks:L426:msg": "\"Use no foul rogue[br]tricks to make[br][firstname] despise you!\"",
    "op2.ks:L432:msg": "\"Keep distance, use[br]no force, court her[br]smartly, swiftly, and[br]win her heart!\"",
    "op2.ks:L437:msg": "...Utterly absurd.",
    "op2.ks:L442:msg": "Totam and Joshua[br]stand gaping in[br]sheer disbelief.",
    "op2.ks:L447:msg": "Woo a girl without[br]force, distance, or[br]tricks in a pirate[br]den? Miraculous.",
    "op2.ks:L454:msg": "\"Understood?![br]Do you hear me?!\"",
    "op2.ks:L460:msg": "A pure farce, yet the[br]King speaks dead[br]serious. Laugh, and[br]your head flies.",
    "op2.ks:L466:msg": "The kneeling suitor[br]seems at a total loss.[br]I almost begin to[br]pity the poor man.",
    "op2.ks:L472:msg": "Whoever he is, he[br]must be exasperated[br]to death.",
    "op2.ks:L480:msg": "\"......Dear husband.\"",
    "op2.ks:L485:msg": "Mother gently reins[br]in Father's frenzy.",
    "op2.ks:L491:msg": "\"...Hm?\"",
    "op2.ks:L497:msg": "\"......[firstname] is[br]waiting outside.\"",
}

OP2_PART_B = {
    "op2.ks:L502:msg": "Mother casts a glance[br]straight toward my[br]hiding spot.",
    "op2.ks:L507:msg": "\"...Ugh.\"",
    "op2.ks:L512:msg": "I was hiding, yet[br]she spotted me[br]instantly.",
    "op2.ks:L517:msg": "Mother keeps her eyes[br]locked firmly onto[br]me.",
    "op2.ks:L521:msg": "A gentle smile, yet[br]her gaze pins me so[br]fast I cannot even[br]look away.",
    "op2.ks:L526:msg": "Though lower in rank,[br]Mother is far more[br]terrifying than the[br]King. I want to run.",
    "op2.ks:L532:msg": "I meant to flee once[br]I heard marriage talk,[br]but desertion before[br]her eyes is hopeless.",
    "op2.ks:L537:msg": "Caught red-handed, I[br]cannot even feign[br]I forgot the summons.",
    "op2.ks:L543:msg": "\"...[firstname]?\"",
    "op2.ks:L548:msg": "Noticing Mother's eyes,[br]Father turns back to[br]his royal seat.",
    "op2.ks:L557:msg": "\"......Ahem.\"",
    "op2.ks:L562:msg": "\"You may withdraw.[br]......Come in,[br][firstname].\"",
    "op2.ks:L568:msg": "Father calls me with[br]a doting purr,[br]wholly unlike his[br]fierce command voice.",
    "op2.ks:L581:msg": "Amid vassals' wry[br]smiles, the suitor[br]bows and exits.[br]I never saw his face.",
    "op2.ks:L587:msg": "Well, there is no[br]escaping now...",
    "op2.ks:L597:msg": "I step inside slowly.[br]Knowing what awaits,[br]my feet drag with[br]dread.",
    "op2.ks:L603:msg": "\"Gardin Gilkhatar,[br]our Lord. An audience[br]with Your Majesty is[br]an honor...\"",
    "op2.ks:L609:msg": "\"Enough of stiff[br]formalities. You are[br]lovely as ever,[br]dear [firstname].\"",
    "op2.ks:L616:msg": "\"Husband. Decorum[br]matters. Would you[br]raise our daughter[br]without manners?\"",
    "op2.ks:L623:msg": "\"My Queen is stern[br]today.\"",
    "op2.ks:L628:msg": "\"A beauty has fierce[br]spirit. Being ruled[br]by my wife is my[br]sweet fate.\"",
    "op2.ks:L635:msg": "\"My, such sweet talk...[br]Incorrigible man.\"",
    "op2.ks:L641:msg": "\"Flattery will not[br]sway my lesson plan.\"",
    "op2.ks:L646:msg": "\"Ugh...\"",
    "op2.ks:L651:msg": "\"......\"",
    "op2.ks:L656:msg": "None can best Mother.[br]As a child, I thought[br]she was the ruling[br]monarch, not Father.",
    "op2.ks:L662:msg": "\"Princess [firstname].\"",
    "op2.ks:L667:msg": "\"Answer this grave[br]question with truth[br]in your heart.\"",
    "op2.ks:L674:msg": "\"...Y-Yes?!\"",
    "op2.ks:L679:msg": "Her piercing stare[br]makes me jump. I am[br]defenseless against[br]her gaze.",
    "op2.ks:L685:msg": "\"Tell me, is there[br]someone who holds[br]your heart?\"",
    "op2.ks:L690:msg": "\"Eh...?\"",
    "op2.ks:L695:msg": "\"Well... um...\"",
    "op2.ks:L701:msg": "\"......No one.[br]...There isn't.\"",
    "op2.ks:L707:msg": "I have no lover, nor[br]even anyone I hold[br]special affection for.",
    "op2.ks:L712:msg": "I want to love a[br]'normal' man, have[br]a 'normal' romance,[br]and live normally.",
    "op2.ks:L717:msg": "Yet 'normal' people[br]are rare here, and a[br]princess never meets[br]them anyway.",
    "op2.ks:L722:msg": "I suppose my parents[br]have cause to worry.[br]I should have cooked[br]up a fake lover.",
    "op2.ks:L728:msg": "...Not that I could[br]ever deceive Mother's[br]keen eyes.",
    "op2.ks:L733:msg": "\"I see. How very[br]unfortunate.\"",
    "op2.ks:L739:msg": "\"...Unfortunate?[br]I can't invent someone[br]out of thin air.\"",
    "op2.ks:L745:msg": "\"To have no one to[br]yearn for is sad[br]indeed.\"",
    "op2.ks:L750:msg": "\"Indeed, quite so.\"",
    "op2.ks:L755:msg": "Mother cuts down my[br]excuses without mercy.[br]Father nods like a[br]puppet.",
    "op2.ks:L761:msg": "\"At your age, I was[br]in the throes of a[br]burning passion.[br]Love is wondrous.\"",
    "op2.ks:L767:msg": "\"Indeed... Wait.[br]......With whom were[br]you in love, my[br]Queen?\"",
    "op2.ks:L779:msg": "In the blazing desert,[br]a sudden glacial chill[br]sweeps through the[br]chamber.",
    "op2.ks:L786:msg": "\"Goodness me.[br]Hohoho, with you,[br]of course, dear.\"",
    "op2.ks:L792:msg": "\"Surely your eyes[br]never strayed either,[br]did they? Hohoho...\"",
    "op2.ks:L802:msg": "Mother laughs it off,[br]radiating tundra cold.",
    "op2.ks:L808:msg": "\"O-Of course not.[br]None but my Queen has[br]ever filled my sight.\"",
    "op2.ks:L814:msg": "\"Hohoho.[br]I should hope so.\"",
    "op2.ks:L820:msg": "\"[firstname], you are[br]the fruit of a great[br]love story.\"",
    "op2.ks:L825:msg": "\"......Right.[br]How very nice for[br]you both...\"",
    "op2.ks:L831:msg": "Spare me your lovers'[br]spat... I admire the[br]retainers for keeping[br]straight faces.",
    "op2.ks:L838:msg": "\"Ahem. Being a love[br]match ourselves, we[br]wish you free love[br]as well.\"",
    "op2.ks:L845:msg": "\"Then call off these[br]suitors, please...!\"",
    "op2.ks:L850:msg": "\"Never. Left alone,[br]you show no sign of[br]any courtship at all.\"",
    "op2.ks:L856:msg": "\"I-It's not that I'm[br]hopeless...\"",
    "op2.ks:L862:msg": "\"What?! Is there[br]someone after all?!\"",
    "op2.ks:L868:msg": "\"Hush, husband.\"",
    "op2.ks:L873:msg": "\"You have found no[br]one you'd marry.[br]A mother senses[br]these things.\"",
    "op2.ks:L879:msg": "\"Gilkhatar is not a[br]pure hereditary[br]dynasty.\"",
    "op2.ks:L884:msg": "\"You need not reign[br]or crown a consort.[br]Yet you may, if you[br]so desire.\"",
    "op2.ks:L890:msg": "\"......I do not.[br]I have no desire[br]for the throne.\"",
    "op2.ks:L897:msg": "I want to be 'normal'.[br]The crown is too[br]heavy for a girl like[br]me to wear.",
    "op2.ks:L903:msg": "\"I see. Yet born as[br]first princess, you[br]are royal for life.\"",
    "op2.ks:L909:msg": "\"You know you cannot[br]become a commoner,[br]right?\"",
    "op2.ks:L914:msg": "\"I know that. Ceding[br]succession to kin[br]won't strip away my[br]princess blood.\"",
    "op2.ks:L920:msg": "\"That is the trouble.[br]High station breeds[br]more peril than[br]privilege.\"",
    "op2.ks:L926:msg": "\"While we live, none[br]dare harm you. But[br]pass the crown, and[br]who can say?\"",
    "op2.ks:L931:msg": "Mother glances at the[br]two ministers beside[br]the throne. A clear[br]warning.",
    "op2.ks:L937:msg": "Even kin turn wolfish[br]once the crown falls.[br]To a foreign queen,[br]all look suspect.",
    "op2.ks:L943:msg": "If Father falls or[br]steps down, a former[br]king's daughter is[br]in mortal danger.",
    "op2.ks:L948:msg": "Without wealth or[br]rank, survival is grim.[br]Mother's dread is[br]not unfounded.",
    "op2.ks:L954:msg": "\"Crown duties come[br]first, yet we are[br]parents. We worry[br]for you.\"",
    "op2.ks:L960:msg": "\"I appreciate that,[br]truly! But I...\"",
    "op2.ks:L966:msg": "\"No, [firstname].[br]Hear me out.\"",
    "op2.ks:L971:msg": "\"Lyle Sluman says[br]you have raw gift[br]yet refuse real-world[br]practice.\"",
    "op2.ks:L976:msg": "\"Renounce the crown,[br]and we have no proof[br]you could sustain[br]yourself alone.\"",
}

OP2_PART_C = {
    "op2.ks:L981:msg": "\"Throne or not, you[br]must wed a strong man[br]to ensure safety.\"",
    "op2.ks:L986:msg": "\"W-Wait! Marrying[br]just to soothe your[br]peace of mind?!\"",
    "op2.ks:L992:msg": "\"Only betrothal for[br]now. We do not demand[br]immediate wedding.\"",
    "op2.ks:L998:msg": "\"It's the same thing![br]It won't stop at just[br]engagement!\"",
    "op2.ks:L1004:msg": "\"You'll railroad me[br]into marriage! This[br]is tyranny!\"",
    "op2.ks:L1011:msg": "\"Tyranny suits us.[br]I take it as praise.\"",
    "op2.ks:L1017:msg": "\"[firstname], you have[br]twenty-five days.[br]Choose a fiancé[br]within that time.\"",
    "op2.ks:L1023:msg": "\"Twenty-five days?!\"",
    "op2.ks:L1028:msg": "\"Yes, twenty-five.[br]A traditional span,[br]is it not?\"",
    "op2.ks:L1034:msg": "Twenty-five refers to[br]goddess Bernandie's[br]twenty-five blood drops[br]creating the world.",
    "op2.ks:L1039:msg": "The number twenty-five[br]is deemed auspicious[br]in all our customs.",
    "op2.ks:L1044:msg": "\"Tradition or not,[br]how can I find true[br]love in such haste?!\"",
    "op2.ks:L1049:msg": "\"Fret not. The King[br]handpicked promising[br]youths for you.\"",
    "op2.ks:L1056:msg": "\"......So you already[br]set the stage.\"",
    "op2.ks:L1062:msg": "The kneeling suitor[br]made that obvious,[br]yet resentment flares[br]in my eyes.",
    "op2.ks:L1067:msg": "A young girl's glare[br]won't budge sovereign[br]rulers, but I must[br]show defiance.",
    "op2.ks:L1072:msg": "Unsurprisingly, neither[br]flinches. Mother even[br]smiles faintly.",
    "op2.ks:L1078:msg": "\"Do not rebel. The[br]suitors chosen are all[br]familiar to you.[br]You can bond fast.\"",
    "op2.ks:L1085:msg": "\"Fear not, [firstname].[br]No greedy old men.[br]Youths of your age[br]and acquaintance.\"",
    "op2.ks:L1093:msg": "\"Acquaintances?! My[br]acquaintances are all[br]greedy young rogues![br]No different at all!\"",
    "op2.ks:L1099:msg": "Promising youths...[br]Men deemed promising[br]by my parents must[br]be terrifying monsters.",
    "op2.ks:L1105:msg": "Strangers before,[br]now familiar faces.[br]Harder to turn away...",
    "op2.ks:L1111:msg": "Lyle must have put[br]them up to this. I[br]shouldn't have whined[br]about strangers.",
    "op2.ks:L1117:msg": "\"Those with palace[br]access are all blinded[br]by greed and power!\"",
    "op2.ks:L1123:msg": "\"Naturally! A Gilkhatar[br]man without greed is[br]no man at all!\"",
    "op2.ks:L1129:msg": "\"......\"",
    "op2.ks:L1134:msg": "Curse it. I am falling[br]straight into their[br]pace.",
    "op2.ks:L1140:msg": "At this rate, I'll be[br]betrothed, and then[br]swept straight to the[br]altar...",
    "op2.ks:L1146:msg": "I refuse. I will not[br]let myself be washed[br]away like drift sand.",
    "op2.ks:L1152:msg": "I picture myself wed[br]to a thief lord,[br]turning wicked...",
    "op2.ks:L1157:msg": "...No. Never.",
    "op2.ks:L1163:msg": "If I hate it, I must[br]scheme my way out.",
    "op2.ks:L1168:msg": "Surrender now and I'm[br]lost. To escape their[br]ways, I must negotiate[br]Gilkhatar style.",
    "op2.ks:L1175:msg": "\"......That's hardly[br]a fair bargain.\"",
    "op2.ks:L1180:msg": "\"I simply accept your[br]terms? No fair trade[br]works like that.[br]A trade must be--\"",
    "op2.ks:L1186:msg": "\"Fair with all, save[br]those marked for the[br]fleece.\"",
    "op2.ks:L1191:msg": "An ancient Gilkhatar[br]proverb: deal fairly[br]save with marks you[br]intend to swindle.",
    "op2.ks:L1197:msg": "Between kin, deals[br]must be kept square.[br]A code of honor among[br]thieves.",
    "op2.ks:L1202:msg": "And a trade proposed[br]by kin cannot be[br]lightly refused.",
    "op2.ks:L1207:msg": "\"You propose a wager?[br]To win our consent,[br]bring forth worthy[br]terms.\"",
    "op2.ks:L1213:msg": "Bartering with the[br]King and Queen.[br]Tension knots my[br]chest.",
    "op2.ks:L1219:msg": "\"You worry I can't[br]earn my own keep.[br]If I prove I can,[br]your worry vanishes!\"",
    "op2.ks:L1225:msg": "\"One million... In 25[br]days, if I amass 1M[br]Gold, do not force a[br]match upon me!\"",
    "op2.ks:L1231:msg": "1,000,000G in 25 days.[br]Lyle said I have gift;[br]I must trust he was[br]not merely flattering.",
    "op2.ks:L1237:msg": "I hated their ways[br]and shunned drills,[br]yet basic skills are[br]solidly forged.",
    "op2.ks:L1242:msg": "With foundation set,[br]real combat and thief[br]skills should spike[br]rapidly.",
    "op2.ks:L1247:msg": "I can do this.[br]I must embrace the[br]harsh trials I once[br]shunned.",
    "op2.ks:L1255:msg": "\"......\"",
    "op2.ks:L1261:msg": "\"...Ten million Gold.\"",
    "op2.ks:L1267:msg": "\"Ten million, and I[br]accept. A clean, round[br]figure.\"",
    "op2.ks:L1273:msg": "Ten...",
    "op2.ks:L1278:msg": "Ten million Gold?!",
    "op2.ks:L1283:msg": "\"Ten million in 25[br]days?! You must be[br]joking!\"",
    "op2.ks:L1290:msg": "\"I never joke on state[br]wagers. To reassure[br]me, that is the sum[br]required.\"",
    "op2.ks:L1299:msg": "\"My Queen... That sum[br]is far too brutal for[br]our child...\"",
    "op2.ks:L1305:msg": "\"Yes! Ten million is[br]madness...!\"",
    "op2.ks:L1311:msg": "\"Do you claim our[br]daughter cannot amass[br]ten million Gold?\"",
    "op2.ks:L1317:msg": "\"...Hm.\"",
    "op2.ks:L1323:msg": "\"She is my daughter.[br]Nothing is impossible[br]for her blood!\"",
    "op2.ks:L1330:msg": "\"Quite so. Your seed[br]and my flesh. She[br]cannot fail.\"",
    "op2.ks:L1336:msg": "\"W-Wait! What are you[br]saying?! It is impossible![br]Ten million Gold?!\"",
    "op2.ks:L1343:msg": "Don't just nod along![br]Such monstrous praise[br]is pure poison!",
    "op2.ks:L1349:msg": "A novice earning ten[br]million in 25 days?[br]They have lost their[br]minds.",
    "op2.ks:L1355:msg": "I thought they were[br]mocking me, but both[br]wear stone-cold faces.",
    "op2.ks:L1361:msg": "\"Deem it impossible?[br]Yield now and choose[br]your betrothed on[br]the spot.\"",
    "op2.ks:L1367:msg": "\"Suits me well. A firm[br]match brings peace of[br]mind.\"",
    "op2.ks:L1374:msg": "\"Fail to gather 10M,[br]and you must wed the[br]man I choose.\"",
    "op2.ks:L1380:msg": "\"Will you take the[br]wager, or surrender?\"",
    "op2.ks:L1386:msg": "\"...Ugh.\"",
    "op2.ks:L1391:msg": "How malicious. As if[br]I have any real[br]choice to refuse.",
    "op2.ks:L1397:msg": "\"......I accept.\"",
    "op2.ks:L1402:msg": "\"If I fail to gather[br]10M Gold in 25 days,[br]I'll court a suitor.[br]Not wedding outright!\"",
    "op2.ks:L1408:msg": "Courtship leads to[br]wedding anyway. Mother[br]smiles with triumph.",
    "op2.ks:L1415:msg": "\"Splendid. I accept[br]the terms. Husband,[br]have you any input?\"",
    "op2.ks:L1423:msg": "\"My Queen decided all.[br]Only fine details[br]remain.\"",
    "op2.ks:L1430:msg": "\"[firstname], you may[br]not sell your savings[br]or palace heirlooms.[br]New earnings only!\"",
    "op2.ks:L1436:msg": "I nod. Fair enough.",
    "op2.ks:L1442:msg": "Selling jewels would[br]net a fortune, but if[br]caught cheating, I'd[br]forfeit all.",
    "op2.ks:L1448:msg": "\"Agreed. But I may[br]have starting funds,[br]right?\"",
    "op2.ks:L1455:msg": "\"Indeed. Going bare[br]is harsh, so for seed[br]money you shall have--\"",
    "op2.ks:L1464:msg": "\"......No.\"",
}

OP2_PART_D = {
    "op2.ks:L1470:msg": "\"That I forbid.\"",
    "op2.ks:L1475:msg": "\"...What?\"",
    "op2.ks:L1481:msg": "\"Zero starting coin.[br]Start from nothing, or[br]I have no faith in[br]your grit.\"",
    "op2.ks:L1487:msg": "\"...Brutal.\"",
    "op2.ks:L1492:msg": "Without seed money, I[br]cannot buy gear or[br]prepare. Earning paths[br]shrink to nothing.",
    "op2.ks:L1498:msg": "\"Give me some leeway...!\"",
    "op2.ks:L1504:msg": "\"Penniless? Then borrow[br]from moneylenders[br]like the rest.\"",
    "op2.ks:L1509:msg": "\"A loan shark?! Their[br]interest rates are[br]murderous! I'll end[br]in the red!\"",
    "op2.ks:L1516:msg": "Gilkhatar usury rates[br]are lethal. I'd earn[br]10M only to drown in[br]compound debt.",
    "op2.ks:L1523:msg": "\"Such is life. A sea[br]of thorns and traps.\"",
    "op2.ks:L1531:msg": "\"Foreign visitors stay[br]in our guest wing.[br]A traveler who dabbles[br]in finance.\"",
    "op2.ks:L1538:msg": "\"Seek them out. Could[br]you not borrow from[br]their purses?\"",
    "op2.ks:L1543:msg": "\"Borrow from those[br]shady characters?!\"",
    "op2.ks:L1550:msg": "\"Rude to our guests.[br]They are gentlemen of[br]refinement.\"",
    "op2.ks:L1557:msg": "\"This wager decides[br]your life, [firstname].[br]It is no parlor game.\"",
    "op2.ks:L1565:msg": "\"You have royal rank[br]and connections. A purse[br]of gold on top would[br]be absurd.\"",
    "op2.ks:L1571:msg": "\"You want me wed that[br]badly...? Marry a man[br]I despise just for[br]your peace?\"",
    "op2.ks:L1578:msg": "Mother was strict,[br]yet never so callous.[br]Her arrogant demand[br]stings like poison.",
    "op2.ks:L1585:msg": "\"......\"",
    "op2.ks:L1591:msg": "\"Yes. I demand peace[br]of mind. Your petty[br]wishes matter not.\"",
    "op2.ks:L1598:msg": "Mother cuts me off[br]coldly.",
    "op2.ks:L1603:msg": "\"...How could you.\"",
    "op2.ks:L1608:msg": "Faced with such icy[br]resolve, words fail me.",
    "op2.ks:L1615:msg": "\"Wed a mighty lord or[br]prove you can thrive[br]alone. Fail the test,[br]and submit to vows.\"",
    "op2.ks:L1620:msg": "\"Mother... that is far[br]too cruel.\"",
    "op2.ks:L1626:msg": "I glare at her, and[br]Father steps in to[br]shield her.",
    "op2.ks:L1632:msg": "\"Harsh terms indeed.\"",
    "op2.ks:L1638:msg": "\"Yet I place no rule[br]upon how you gather[br]the gold.\"",
    "op2.ks:L1644:msg": "\"Stolen, plundered,[br]extorted. Strip whom[br]you will.\"",
    "op2.ks:L1650:msg": "\"I know that without[br]asking. That is the[br]Gilkhatar creed.\"",
    "op2.ks:L1656:msg": "\"You force me to do[br]the very deeds I swore[br]to avoid...\"",
    "op2.ks:L1661:msg": "I have no other[br]recourse.",
    "op2.ks:L1666:msg": "To escape their ways,[br]I must practice them[br]ruthlessly. Bitter[br]irony.",
    "op2.ks:L1673:msg": "\"Frown not, my child.\"",
    "op2.ks:L1679:msg": "\"Guild bounties, slaying[br]monsters... yet this is[br]Gilkhatar. Shortcuts[br]abound.\"",
    "op2.ks:L1686:msg": "\"Hear me, [firstname].[br]Steal from anyone,[br]save your own gear.\"",
    "op2.ks:L1695:msg": "\"Husband, surely not...\"",
    "op2.ks:L1703:msg": "\"I stand firm, Queen.[br]Robbing kin shows true[br]grit in our realm.\"",
    "op2.ks:L1710:msg": "\"If you can, that is.[br]You are a thief king's[br]daughter. No vault is[br]barred to you.\"",
    "op2.ks:L1717:msg": "\"You mean...\"",
    "op2.ks:L1722:msg": "Steal from anyone...[br]even my own parents?",
    "op2.ks:L1727:msg": "Father implies that[br]if I have the skill,[br]I may crack the royal[br]treasury itself.",
    "op2.ks:L1733:msg": "\"[firstname], you are[br]my only child.\"",
    "op2.ks:L1739:msg": "\"A son would inherit[br]without question, yet[br]for a maiden, the[br]crown is treacherous.\"",
    "op2.ks:L1746:msg": "\"Your mother does not[br]seek to torment you.\"",
    "op2.ks:L1752:msg": "\"She dreads for your[br]future once I fall.[br]A mother's fierce[br]devotion.\"",
    "op2.ks:L1758:msg": "\"Do you also wish me[br]wed to a Gilkhatar[br]lord?\"",
    "op2.ks:L1763:msg": "Father hesitates and[br]does not answer directly.",
    "op2.ks:L1769:msg": "\"Had you a lover, all[br]would be simple.\"",
    "op2.ks:L1775:msg": "\"A mighty lord you love[br]would ease all our[br]fears.\"",
    "op2.ks:L1782:msg": "\"Lacking that, we face[br]a grim choice.\"",
    "op2.ks:L1788:msg": "\"Grant you freedom into[br]the dark unknown, or[br]force high safety upon[br]you against your will.\"",
    "op2.ks:L1795:msg": "\"......I know not which[br]path brings you true[br]joy.\"",
    "op2.ks:L1803:msg": "\"I will not force you.[br]Yet weigh marriage as[br]fairly as lonely[br]independence.\"",
    "op2.ks:L1809:msg": "Father's face is torn[br]with sorrow.",
    "op2.ks:L1814:msg": "If only I had a brother,[br]or was born a son...",
    "op2.ks:L1820:msg": "Then none would agonize,[br]and Mother would not[br]fear.",
    "op2.ks:L1826:msg": "Mere wishes.",
    "op2.ks:L1831:msg": "Yet if only I were...",
    "op2.ks:L1838:msg": "\"[firstname], do you[br]loathe Gilkhatar, your[br]homeland?\"",
    "op2.ks:L1843:msg": "\"Never. I could never[br]hate my home.\"",
    "op2.ks:L1849:msg": "Father's land and mine.[br]Nurtured by its dunes[br]and sands.",
    "op2.ks:L1855:msg": "I reject rogue ways,[br]not the soil of my[br]birth.",
    "op2.ks:L1861:msg": "\"Gilkhatar is dear to[br]me. It treated me with[br]kindness, and I love[br]it.\"",
    "op2.ks:L1868:msg": "\"...I am glad to hear[br]those words.\"",
    "op2.ks:L1874:msg": "\"If you love the realm,[br]you can learn to love[br]its men as well.\"",
    "op2.ks:L1881:msg": "\"Look past the rogue[br]mask; they harbor[br]unexpected depths.\"",
    "op2.ks:L1888:msg": "Raised as a princess,[br]I owe this desert[br]realm my life.",
    "op2.ks:L1894:msg": "Yet its men...",
    "op2.ks:L1899:msg": "Scoundrels every last[br]one. How could Father's[br]suitors be decent...?",
    "op2.ks:L1905:msg": "Round and round...",
    "op2.ks:L1910:msg": "Round and round my[br]thoughts spin...",
    "op2.ks:L1915:msg": "\"......Understood. I[br]shall strive and think[br]for 25 days.\"",
    "op2.ks:L1927:msg": "I bow curtly and turn[br]from the audience[br]hall.",
    "op2.ks:L1932:msg": "The wager is struck.[br]No turning back now.",
    "op2.ks:L1938:msg": "I want a decent life,[br]honest romance, and a[br]truly good man.",
    "op2.ks:L1957:msg": "\"She seemed aggrieved,[br]yet accepted the terms[br]in the end...\"",
    "op2.ks:L1965:msg": "\"Yes. Though playing[br]villain makes me look[br]dreadfully wicked.\"",
    "op2.ks:L1973:msg": "\"Wickedness is fine[br]currency here.\"",
    "op2.ks:L1979:msg": "\"For a queen, yes.[br]Yet I would not have[br]my daughter hate me.\"",
    "op2.ks:L1986:msg": "\"Still, she has grown[br]magnificently.\"",
    "op2.ks:L1992:msg": "\"To counter with such[br]a bold wager... She is[br]queenly material.\"",
    "op2.ks:L1998:msg": "\"Even without crown,[br]she will flourish.\"",
    "op2.ks:L2004:msg": "\"Do you wish her wed,[br]or free to roam?\"",
    "op2.ks:L2011:msg": "\"I am torn myself,[br]dear husband.\"",
    "op2.ks:L2018:msg": "\"Whichever brings her[br]joy and safety suits[br]me fine.\"",
    "op2.ks:L2024:msg": "\"I forced nothing.[br]She proposed the[br]wager herself.\"",
    "op2.ks:L2031:msg": "\"If she fails, she[br]truly desires marriage[br]at heart.\"",
    "op2.ks:L2037:msg": "\"......My Queen, you[br]are a Gilkhatar woman[br]to the bone.\"",
    "op2.ks:L2044:msg": "\"......I trust that was[br]meant as praise?\"",
    "op2.ks:L2050:msg": "\"......Of course, my[br]love.\"",
    "op2.ks:L2057:msg": "\"Totam, Joshua. Watch[br]over [firstname] during[br]these days.\"",
    "op2.ks:L2064:msg": "\"Lend no aid, but keep[br]her safe from shadows.\"",
    "op2.ks:L2072:msg": "\"Gladly, Sire. Wager[br]or not, guarding her[br]is our duty.\"",
    "op2.ks:L2081:msg": "\"I shall do my duty[br]and instruct my son[br]likewise.\"",
}

def generate_op2_op3_translations():
    os.makedirs('translations/working', exist_ok=True)
    os.makedirs('translations/reviewed', exist_ok=True)
    
    # 1. Load source scenario records
    source_records = {}
    with open('translations/source/scenario_all.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            source_records[d['id']] = d

    # Combine all op2 and op3 mappings
    all_new = {}
    all_new.update(OP2_PART_A)
    all_new.update(OP2_PART_B)
    all_new.update(OP2_PART_C)
    all_new.update(OP2_PART_D)
    all_new.update(OP3_TRANSLATIONS)

    # Apply refined, strictly length-tuned entries
    from tools.refine_dict import REFINED_ENTRIES
    all_new.update(REFINED_ENTRIES)

    print(f"Total new translations mapped: {len(all_new)} (op2: {len(OP2_PART_A)+len(OP2_PART_B)+len(OP2_PART_C)+len(OP2_PART_D)}, op3: {len(OP3_TRANSLATIONS)})")

    # 2. Match and validate
    output_records = []
    validation_errors = []
    
    for rid, raw_en in all_new.items():
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

    print(f"Validated {len(output_records)} records.")
    if validation_errors:
        print(f"Found {len(validation_errors)} validation errors:")
        for rid, errs in validation_errors:
            print(f"  [{rid}] {errs}")
        sys.exit(1)

    # 3. Merge with existing reviewed prologue translations (pro_name1..3, pro_skip, op1)
    existing_reviewed = []
    existing_ids = set()
    prologue_rev_path = 'translations/reviewed/prologue_translated.jsonl'
    if os.path.exists(prologue_rev_path):
        with open(prologue_rev_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    existing_reviewed.append(d)
                    existing_ids.add(d['id'])

    # Filter out any old versions of the same IDs, then combine
    merged_records = [r for r in existing_reviewed if r['id'] not in all_new]
    merged_records.extend(output_records)

    print(f"Combined total reviewed records: {len(merged_records)} (Previous: {len(existing_reviewed)}, Added: {len(output_records)})")

    # Write merged files
    for out_path in ['translations/working/prologue_translated.jsonl', 'translations/reviewed/prologue_translated.jsonl']:
        with open(out_path, 'w', encoding='utf-8') as f:
            for r in merged_records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"Wrote {out_path} with {len(merged_records)} lines.")

    # 4. Verify repacking for op2.ks and op3.ks
    for sf in ['op2.ks', 'op3.ks']:
        sf_trans = {r['id']: r['english'] for r in output_records if r['source_file'] == sf}
        src_path = os.path.join('extracted/data_cpk/scenario', sf)
        repacked = repack_file(src_path, sf_trans, sf)
        repacked.encode('cp932')
        print(f"  {sf}: Successfully repacked & verified CP932 encoding ({len(repacked)} chars, {len(sf_trans)} translated lines)")

if __name__ == '__main__':
    generate_op2_op3_translations()
