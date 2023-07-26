import json
from xmlrpc import client
from connection import *

server_url = 'https://tstodoo.fgmed.org'
db_name = 'tstodoo.fgmed.org'
username = 'admin'
password = 'tstpass'
common = client.ServerProxy('%s/xmlrpc/2/common' % server_url)
user_id = common.authenticate(db_name, username, password, {})
models = client.ServerProxy('%s/xmlrpc/2/object' % server_url, allow_none=True)

cursos_times = models.execute_kw(db_name, user_id, password, "fgmed.courses.time", "search_read", [
    [['id', '>', 0]]], {'fields': ['name', 'time']})
modvalues = {"IN": "intensiva", "EX": "extensiva", "OU": "ouro"}

"""
variantid = 225
pmethodlist = [84, 85, 86, 87, 88, 89, 156, 157, 158, 159, 160, 161, 193]
models.execute_kw(db_name, user_id, password, 'product.product', 'write', [
                  [225], {'course_payment_methods_ids': pmethodlist}])

variantid = 225
models.execute_kw(db_name, user_id, password, 'product.product', 'write', [[variantid], {
                  'course_modality': 'intensiva', 'course_conclusion': 6, 'course_base_time_id': 1, 'course_itrn_time_id': 2,'course_payment_methods_ids': pmethodlist}])
"""
print(cursos_times)
avaliabletimes = {}
avaliabletimes[0] = {'id': False, 'name': False}
for timecourse in cursos_times:
    avaliabletimes[timecourse['time']] = {
        'id': timecourse['id'], 'name': timecourse['name']}
print(avaliabletimes)
print("- - - - - - - - - -")


def paymentCondition(type, time):
    conditionlist = []
    conditions = models.execute_kw(db_name, user_id, password, "account.payment.term", "search_read", [
        [['payment_term_type', '=', type], ['payment_term_count', '<=', time]]], {'fields': ['id']})
    for condition in conditions:
        conditionlist.append(condition['id'])
    return (conditionlist)


cursos = models.execute_kw(db_name, user_id, password, "product.template", "search_read", [
                           [['description', '!=', ''], ['categ_id', '=', 9]]], {'fields': ['categ_id', 'name', 'description']})
lista_tempos = {}
for curso in cursos:
    tempdescr = json.loads(curso['description'])
    print(tempdescr)
    print(curso['id'], "  --  ", curso['categ_id'], "  --  ", curso['name'])
    for modalidade in tempdescr:
        print(modalidade)
        code = modalidade
        vcodeparts = code.split("_")
        insertedData = {}
        variante = models.execute_kw(db_name, user_id, password, "product.product", "search_read", [
                                     [['default_code', '=', code]]], {'fields': ['name']})
        course_base_time = avaliabletimes[int(
            tempdescr[modalidade]['courseTimes'][0])]
        course_prat_time = avaliabletimes[int(
            tempdescr[modalidade]['courseTimes'][1])]
        checkout_max = tempdescr[modalidade]['paymentAcept']['checkout'][1]
        recurrence_max = tempdescr[modalidade]['paymentAcept']['recurrence'][1]
        accepted_rec = paymentCondition('recurrence', recurrence_max)
        # accepted_rec = paymentCondition('future-recurrence', recurrence_max)
        accepted_checkout = paymentCondition('checkout', checkout_max)
        accepted_checkout_misto = paymentCondition(
            'checkout-misto', checkout_max)
        accepted_checkout_boleto = paymentCondition(
            'checkout-pix', checkout_max)
        payment_accepted = accepted_rec + accepted_checkout + accepted_checkout_boleto
        insertedData['course_modality'] = modvalues[vcodeparts[1]]
        insertedData['course_conclusion'] = int(recurrence_max)
        if (course_base_time['id'] > 0):
            insertedData['course_base_time_id'] = course_base_time['id']
        if (course_prat_time['id'] > 0):
            insertedData['course_itrn_time_id'] = course_prat_time['id']
        insertedData['course_payment_methods_ids'] = payment_accepted

        print(modvalues[vcodeparts[1]])
        # 'course_modality': modvalues[vcodeparts[1]], 'course_conclusion': recurrence_max, 'course_base_time_id': course_base_time, 'course_itrn_time_id': course_prat_time, 'course_payment_methods_ids': pmethodlist
        if (len(variante) > 0):
            print("Achei a variante")
            print(variante[0]['id'])
            atualizado = models.execute_kw(db_name, user_id, password, 'product.product', 'write', [
                                           [variante[0]['id']], insertedData])
            print("atualizei")
            print(atualizado)
        else:
            print("Não Achei a variante")

        """ print("\tCódigo:", code, " - tempo de conclusão", recurrence_max, " - Tempo Base:", course_base_time['id'], " - Tempo de Prática",
              course_prat_time['id'], " - Tmax checkout", checkout_max, " - tmax recorrencia", recurrence_max)
        print("_____V")
        print(payment_accepted)
        print('_____^')
        # models.execute_kw(db, uid, password, 'res.partner', 'write', [[variante[id]], {'name': "Newer partner"}])"""

# print(lista_tempos)
