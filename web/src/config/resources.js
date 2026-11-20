// 资源配置决定列表、查询条件及新增/编辑表单。
const text = (key, label, required = true, type = 'text') => ({ key, label, required, type })
export const resources = {
  employees: {
    label: '员工管理', icon: 'users', hint: '按页浏览员工资料，维护工号、部门与联系方式。',
    columns: [['id', 'ID'], ['emp_name', '姓名'], ['emp_no', '工号'], ['department', '部门'], ['phone', '联系电话']],
    fields: [text('emp_name', '姓名'), text('emp_no', '工号'), text('department', '部门'), text('phone', '联系电话', false, 'tel')],
    deletable: true,
  },
  attendance: {
    label: '考勤记录', icon: 'clock', hint: '按员工 ID 或考勤日期查询。两者同时填写时，后端优先使用员工 ID。',
    filters: [text('emp_id', '员工 ID', false, 'number'), text('attend_date', '考勤日期', false, 'date')],
    columns: [['id', 'ID'], ['emp_id', '员工 ID'], ['attend_date', '考勤日期'], ['check_in', '上班时间'], ['check_out', '下班时间'], ['status', '状态']],
    fields: [text('emp_id', '员工 ID', true, 'number'), text('attend_date', '考勤日期', true, 'date'), text('check_in', '上班时间', true, 'time'), text('check_out', '下班时间', true, 'time'), text('status', '考勤状态')],
    immutable: ['emp_id', 'attend_date'], defaults: { status: '正常' },
  },
  leaves: {
    label: '请假申请', icon: 'file', hint: '按员工 ID 或请假开始日期查询。两者同时填写时，后端优先使用员工 ID。',
    filters: [text('emp_id', '员工 ID', false, 'number'), text('start_date', '开始日期', false, 'date')],
    columns: [['id', 'ID'], ['emp_id', '员工 ID'], ['leave_type', '请假类型'], ['start_date', '开始日期'], ['end_date', '结束日期'], ['reason', '原因'], ['audit_status', '审核状态']],
    fields: [text('emp_id', '员工 ID', true, 'number'), text('leave_type', '请假类型'), text('start_date', '开始日期', true, 'date'), text('end_date', '结束日期', true, 'date'), text('reason', '请假原因')],
    editFields: [text('audit_status', '审核状态')], immutable: ['emp_id'], defaults: { leave_type: '年假' },
  },
  contacts: {
    label: '企业通讯录', icon: 'book', hint: '按姓名查找联系人，维护部门与联系电话。',
    filters: [text('name', '联系人姓名')],
    columns: [['id', 'ID'], ['name', '姓名'], ['phone', '联系电话'], ['department', '部门'], ['remark', '备注']],
    fields: [text('name', '姓名'), text('phone', '联系电话', true, 'tel'), text('department', '部门'), text('remark', '备注', false)],
    deletable: true,
  },
}
