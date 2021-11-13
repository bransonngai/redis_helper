# namespace
# NAMESPACE_REDIS = 'DASHBOARD_3201_'
# NAMESPACE_RDIC = NAMESPACE_REDIS + 'RDIC'
# NAMESPACE_RRDIC = NAMESPACE_REDIS + 'RRDIC'
# NAMESPACE_RTUP_DIC = NAMESPACE_REDIS + 'RTUP_DIC'
# NAMESPACE_SUB_SYMLIST = NAMESPACE_REDIS + 'SUB_SYMLIST'
# NAMESPACE_SUB_ULIST = NAMESPACE_REDIS + 'SUB_ULIST'
# NAMESPACE_SUB_DLIST = NAMESPACE_REDIS + 'SUB_DLIST'

# storing target list
# gateway.rdic_inited: bool = False
# gateway.rdic: dict = r_mgr.get(NAMESPACE_RDIC)  # warrant_target
# gateway.rrdic: dict = r_mgr.get(NAMESPACE_RRDIC)  # warrant_target reverse pairs, for quickly look up underlying
# gateway.sub_symlist: List[str] = (lambda: [] if r_mgr.get(NAMESPACE_SUB_SYMLIST) == '' else r_mgr.get(
#     NAMESPACE_SUB_SYMLIST))()  # internal record of subscribing symlist
# gateway.sub_ulist: List[str] = (lambda: [] if r_mgr.get(NAMESPACE_SUB_ULIST) == '' else r_mgr.get(
#     NAMESPACE_SUB_ULIST))()  # underlying list to subscribe
# gateway.sub_dlist: List[str] = (
#     lambda: [] if r_mgr.get(NAMESPACE_SUB_DLIST) == '' else r_mgr.get(NAMESPACE_SUB_DLIST))()  # deri list to subscibe
# gateway.rtup_dic: Dict[str, tuple] = (lambda: {} if r_mgr.get(NAMESPACE_RTUP_DIC) == '' else r_mgr.get(
#     NAMESPACE_RTUP_DIC))()  # storing a tuple of calculation (e.g. net positions)

