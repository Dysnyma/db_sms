"""中文表格组件（基于 st-aggrid），全功能配置"""

import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

_LOCALE_TEXT = {
    # 排序
    "sortAscending": "升序",
    "sortDescending": "降序",
    "unSort": "取消排序",
    # 列操作
    "columns": "列",
    "filter": "筛选",
    "searchOoo": "搜索…",
    "noMatches": "无匹配",
    "pinColumn": "固定列",
    "pinLeft": "固定在左",
    "pinRight": "固定在右",
    "noPin": "不固定",
    "hideColumn": "隐藏列",
    "autoSizeThisColumn": "自适应列宽",
    "autoSizeAllColumns": "自适应所有列",
    "resetColumns": "重置列",
    # 复制 / 粘贴
    "copy": "复制",
    "copyWithHeaders": "含表头复制",
    "copyWithGroupHeaders": "含分组头复制",
    "ctrlC": "Ctrl+C",
    "ctrlX": "Ctrl+X",
    "paste": "粘贴",
    "copyToClipboard": "复制到剪贴板",
    # 导出
    "export": "导出",
    "csvExport": "导出 CSV",
    "excelExport": "导出 Excel",
    # 右键菜单
    "addRow": "添加行",
    "deleteRow": "删除行",
    "clearFilter": "清除筛选",
    # 分页
    "page": "页",
    "more": "更多",
    "to": "至",
    "of": "共",
    "next": "下一页",
    "previous": "上一页",
    "first": "首页",
    "last": "末页",
    "totalRows": "总行数：",
    "pageSize": "每页行数：",
    # 统计（状态栏 + 分组汇总）
    "avg": "平均值",
    "min": "最小值",
    "max": "最大值",
    "sum": "总和",
    "count": "计数",
    "group": "分组",
    "agg": "聚合",
    "totalAndFilteredRows": "行数",
    "moreRows": "更多行",
    "selectedRows": "已选行",
    # 筛选条件
    "blank": "空白",
    "notBlank": "非空白",
    "notEqual": "不等于",
    "equals": "等于",
    "lessThan": "小于",
    "greaterThan": "大于",
    "lessThanOrEqual": "小于等于",
    "greaterThanOrEqual": "大于等于",
    "inRange": "范围",
    "contains": "包含",
    "notContains": "不包含",
    "startsWith": "开头是",
    "endsWith": "结尾是",
    "true": "是",
    "false": "否",
    # 筛选面板
    "applyFilter": "确定",
    "clearFilter": "清除",
    "reset": "重置",
    "filterOoo": "筛选…",
    "loadingOoo": "加载中…",
    "noRowsToShow": "暂无数据",
    # 列设置面板
    "pinnedColumns": "固定列：",
    "valueAggregation": "值聚合",
    "rowGroup": "行分组",
    "dropRowGroupHere": "拖入此处进行按列分组",
    # 分组面板
    "rowGroupColumns": "拖入此处进行分组…",
    "rowGroupColumnsEmptyMessage": "拖拽列头到此处按该列分组",
    "valueColumns": "值列",
    "pivotMode": "透视模式",
    "pivotColumnGroupTotals": "合计",
}


def st_ag(df, **kwargs):
    """
    全功能中文表格组件。

    参数
    ----
    df : pd.DataFrame
        要显示的数据
    use_container_width : bool
        是否撑满容器宽度（默认 True）
    height : int
        表格高度（默认 400，None 为自动）
    pagination : bool
        是否启用分页（默认 True）
    page_size : int
        每页行数（默认 25）
    selection : str | None
        行模式："single" | "multiple"（默认 None 不启用勾选）
    groupable : bool
        是否允许拖拽分组（默认 False）
    """
    use_container_width = kwargs.pop("use_container_width", True)
    height = kwargs.pop("height", 400)
    pagination = kwargs.pop("pagination", True)
    page_size = kwargs.pop("page_size", 25)
    selection = kwargs.pop("selection", None)
    groupable = kwargs.pop("groupable", False)

    # ── 统一数值类型，避免 [object Object] ──
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    gb = GridOptionsBuilder.from_dataframe(df)

    # ── 全局列配置 ──
    gb.configure_default_column(
        sortable=True,
        filterable=True,
        resizable=True,
        groupable=groupable,
        editable=False,
        filter="agTextColumnFilter",
        menuTabs=["generalMenuTab", "filterMenuTab"],
    )

    # ── 数值列特殊配置（避免 [object Object]） ──
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            gb.configure_column(
                col,
                type=["numericColumn"],
                filter="agNumberColumnFilter",
            )

    # ── 分页 ──
    if pagination:
        gb.configure_pagination(enabled=True, paginationPageSize=page_size)
        gb.configure_grid_options(paginationPageSizeSelector=[10, 25, 50, 100])

    # ── 行选择 ──
    if selection:
        gb.configure_selection(
            selection_mode=selection,
            use_checkbox=True,
            pre_selected_rows=[],
        )

    # ── 侧边栏（筛选面板 + 列管理） ──
    gb.configure_side_bar(filters_panel=True, columns_panel=True)

    # ── 底部状态栏（统计：平均值、最小值、最大值、总和、计数） ──
    gb.configure_grid_options(
        enableStatusBar=True,
        statusBar={
            "statusPanels": [
                {
                    "statusPanel": "agTotalAndFilteredRowCountComponent",
                    "key": "totalRowCountPanel",
                    "label": "行数：",
                },
                {
                    "statusPanel": "agSelectedRowCountComponent",
                    "key": "selectedRowCountPanel",
                    "label": "已选：",
                },
                {
                    "statusPanel": "agAggregationComponent",
                    "key": "aggregationPanel",
                    "statusPanelParams": {
                        "aggFuncs": ["count", "min", "max", "avg", "sum"],
                    },
                },
            ],
        },
    )

    # ── 全局选项 ──
    gb.configure_grid_options(
        localeText=_LOCALE_TEXT,
        enableCellTextSelection=True,
        ensureDomOrder=True,
        enableCellContentClipboard=True,
        clipboardDelimiter="\t",
        rowHeight=35,
        headerHeight=38,
        suppressMovableColumns=False,
        animateRows=False,
    )

    grid_options = gb.build()

    # ── 渲染 ──
    return AgGrid(
        df,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=use_container_width,
        height=height,
        highlight_selected_on_render=False,
        theme="streamlit",
        enable_enterprise_modules=True,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.NO_UPDATE,
        **kwargs,
    )
