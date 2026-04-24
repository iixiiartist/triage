# Eval set spot-check samples

One random test example per intent class. Review for label correctness.

Flag any mislabels in `eval/known_errors.md` — do NOT edit test.jsonl.


## account_access

- **id:** `bitext_aa6d1dd8c69e`
- **lang:** en
- **priority:** P2
- **route:** account_security
- **text:** assistance notifying of a signup problem

## billing_dispute

- **id:** `bitext_2f06fb051e87`
- **lang:** en
- **priority:** P2
- **route:** billing_team
- **text:** i try to inform of an error with online payments

## billing_question

- **id:** `bitext_153c88b2a7cf`
- **lang:** en
- **priority:** P3
- **route:** billing_team
- **text:** help seeing the early termination fee

## complaint

- **id:** `bitext_9b24ced7f34a`
- **lang:** en
- **priority:** P3
- **route:** human_escalation
- **text:** I want assistance to make a consumer claim

## compliment

- **id:** `bitext_72d923aa3e47`
- **lang:** en
- **priority:** P4
- **route:** product_feedback
- **text:** how could I leave a review for your products?

## delete_account

- **id:** `bitext_b009d643c3a1`
- **lang:** en
- **priority:** P3
- **route:** account_security
- **text:** remove gold account

## escalation_request

- **id:** `bitext_7f1ebc8a94f3`
- **lang:** en
- **priority:** P1
- **route:** human_escalation
- **text:** I need to talk to an operator, could I get some help?

## how_to

- **id:** `bitext_409356691bdd`
- **lang:** en
- **priority:** P3
- **route:** technical_support
- **text:** I don't know what I have to do to purchase something

## order_status

- **id:** `bitext_10fc58076956`
- **lang:** en
- **priority:** P3
- **route:** returns_and_shipping
- **text:** i need help to change an item of purchase {{Order Number}}

## other

- **id:** `bitext_7693065a0075`
- **lang:** en
- **priority:** P3
- **route:** human_escalation
- **text:** I have a question about opening a {{Account Type}} account

## out_of_scope

- **id:** `massive_fr_785f999bffaf`
- **lang:** fr
- **priority:** P3
- **route:** auto_close
- **text:** tweet à amazon à propos de la livraison tardive de mon t. v.

## password_reset

- **id:** `bitext_7698fe3c2545`
- **lang:** en
- **priority:** P3
- **route:** account_security
- **text:** i have problesm with my forgotten pwd

## refund_request

- **id:** `bitext_3d5fdf7cf0b7`
- **lang:** en
- **priority:** P3
- **route:** billing_team
- **text:** need assistance receiving rebates of my money

## shipping_question

- **id:** `bitext_c41756a46205`
- **lang:** en
- **priority:** P3
- **route:** returns_and_shipping
- **text:** wanna check how soon can i expect my article

## update_profile

- **id:** `bitext_c4fffd94c9ca`
- **lang:** en
- **priority:** P3
- **route:** account_security
- **text:** I don't know how to cancel my subscription to the newsletter
